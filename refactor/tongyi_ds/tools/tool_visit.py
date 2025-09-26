import asyncio
import json
import os
import re
import time
from typing import Dict, Iterable, List, Optional, Tuple, Union

import requests
import tiktoken
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.async_configs import BrowserConfig
from crawl4ai.processors.pdf import PDFContentScrapingStrategy, PDFCrawlerStrategy
from openai import OpenAI
from qwen_agent.tools.base import BaseTool, register_tool

from refactor.tongyi_ds.constants import EVIDENCE_JSON_END, EVIDENCE_JSON_START
from refactor.tongyi_ds.tools.tool_crawl import Crawler


# ---------------- util ----------------
def truncate_to_tokens(text: str, max_tokens: int = 95000) -> str:
    enc = tiktoken.get_encoding("cl100k_base")
    toks = enc.encode(text)
    return text if len(toks) <= max_tokens else enc.decode(toks[:max_tokens])


def is_pdf_url(u: str) -> bool:
    if u.lower().strip().endswith(".pdf"):
        return True
    try:
        r = requests.head(u, allow_redirects=True, timeout=8)
        ct = r.headers.get("Content-Type", "")
        return "pdf" in ct.lower()
    except Exception:
        return False


def pick_markdown(result) -> str:
    md = ""
    if getattr(result, "markdown", None):
        # prefer fit_markdown if available, fallback to raw_markdown
        md = getattr(result.markdown, "fit_markdown", "") or getattr(
            result.markdown, "raw_markdown", ""
        )
    return md or ""


# ---------------- tool ----------------
@register_tool("visit", allow_overwrite=True)
class Visit(BaseTool):
    name = "visit"
    description = "Visit webpage(s) and return the summary of the content."
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": ["string", "array"],
                "items": {"type": "string"},
                "minItems": 1,
                "description": "The URL(s) of the webpage(s) to visit. Can be a single URL or an array of URLs.",
            },
            "goal": {
                "type": "string",
                "description": "The goal of the visit for webpage(s).",
            },
        },
        "required": ["url", "goal"],
    }

    def call(self, params: Union[str, dict], **kwargs) -> str:
        try:
            url = params["url"]
            goal = params["goal"]
        except Exception:
            return "[Visit] Invalid request format: Input must be a JSON object containing 'url' and 'goal' fields"

        os.makedirs("log", exist_ok=True)

        if isinstance(url, str):
            response = asyncio.run(self._read_and_summarize(url, goal))
        else:
            response_blocks = []
            assert isinstance(url, List)
            start_time = time.time()
            for item in url:
                if time.time() - start_time > 900:
                    response_blocks.append(self._build_empty_response(item, goal))
                    continue
                try:
                    response_blocks.append(
                        asyncio.run(self._read_and_summarize(item, goal))
                    )
                except Exception as exc:
                    response_blocks.append(f"Error fetching {item}: {exc}")
            response = "\n=======\n".join(response_blocks)

        preview = response[:500] + ("..." if len(response) > 500 else "")
        print(f"[visit] Summary length {len(response)}; preview: {preview}")
        return response.strip()

    # ---------------- core with Crawl4AI ----------------
    async def _read_and_summarize(self, url: str, goal: str) -> str:
        is_pdf = is_pdf_url(url)

        if is_pdf:
            text, meta = await self._fetch_with_crawl4ai(url, pdf=True)
        else:
            text, meta = await self._fetch_with_jina_then_crawl4ai(url)

        if not self._is_valid_content(text):
            return self._build_empty_response(url, goal)

        truncated = truncate_to_tokens(text, max_tokens=95000)
        summary = self._summarize_content(
            truncated,
            goal,
            self.call_server,
            int(os.getenv("VISIT_SERVER_MAX_RETRIES", 1)),
        )
        if summary:
            return self._format_summary(url, goal, summary)

        fallback = self._fallback_extract(truncated, goal)
        return self._format_summary(url, goal, fallback)

    async def _fetch_with_jina_then_crawl4ai(self, url: str) -> Tuple[str, Dict]:
        try:
            jina_text = await asyncio.to_thread(self._fetch_via_jina, url)
        except Exception as exc:  # noqa: BLE001
            print(f"[visit] Jina fetch error for {url}: {exc}")
            jina_text = ""

        if self._is_valid_content(jina_text):
            print(f"[visit] Content fetched via Jina for {url}")
            return jina_text, {"source": "jina"}

        print(f"[visit] Jina returned empty for {url}, fallback to Crawl4AI")
        return await self._fetch_with_crawl4ai(url, pdf=False)

    def _fetch_via_jina(self, url: str) -> str:
        crawler = Crawler()
        article = crawler.crawl(url)
        if not article:
            return ""
        markdown = article.to_markdown()
        return markdown or ""

    async def _fetch_with_crawl4ai(self, url: str, pdf: bool) -> Tuple[str, Dict]:
        browser_cfg = BrowserConfig(headless=True, verbose=False)
        if pdf:
            pdf_scraping = PDFContentScrapingStrategy(
                extract_images=False,
                save_images_locally=False,
                batch_size=4,
            )
            pdf_strategy = PDFCrawlerStrategy()
            run_cfg = CrawlerRunConfig(scraping_strategy=pdf_scraping)
            async with AsyncWebCrawler(
                config=browser_cfg, crawler_strategy=pdf_strategy
            ) as crawler:
                result = await crawler.arun(url=url, config=run_cfg)
        else:
            run_cfg = CrawlerRunConfig()
            async with AsyncWebCrawler(config=browser_cfg) as crawler:
                result = await crawler.arun(url=url, config=run_cfg)

        if not result or not result.success:
            print(f"[visit] Crawl4AI fetch failed for {url}")
            return "", {}

        text = pick_markdown(result)
        meta = getattr(result, "metadata", {}) or {}
        return text, meta

    # ---------------- original summarization helpers ----------------
    def call_server(self, msgs):
        api_key = os.environ.get("API_KEY")
        url_llm = os.environ.get("API_BASE")
        model_name = os.environ.get("SUMMARY_MODEL_NAME", "")
        if not (api_key and url_llm and model_name):
            return ""

        client = OpenAI(api_key=api_key, base_url=url_llm)
        try:
            chat_response = client.chat.completions.create(
                model=model_name,
                messages=msgs,
                temperature=0.7,
            )
        except Exception:
            return ""
        if not chat_response.choices:
            return ""
        content = chat_response.choices[0].message.content or ""
        left = content.find("{")
        right = content.rfind("}")
        if left != -1 and right != -1 and left <= right:
            return content[left : right + 1]
        return content

    @staticmethod
    def _is_valid_content(content: Optional[str]) -> bool:
        return bool(content and len(content.strip()) > 0)

    def _safe_json_loads(self, payload: str) -> Optional[Dict[str, str]]:
        if not payload:
            return None
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        evidence = data.get("evidence")
        summary = data.get("summary")
        if not evidence or not summary:
            return None
        return {
            "evidence": str(evidence),
            "summary": str(summary),
            "rational": str(data.get("rational", "")),
        }

    def _summarize_content(
        self, content: str, goal: str, summarizer, max_retries: int
    ) -> Optional[Dict[str, str]]:
        from refactor.tongyi_ds.prompts import EXTRACTOR_PROMPT

        prompt = EXTRACTOR_PROMPT.format(webpage_content=content, goal=goal)
        messages = [{"role": "user", "content": prompt}]
        attempt = 0
        truncated = content
        while attempt < 3:
            raw = summarizer(messages)
            if not raw:
                attempt += 1
                truncated = (
                    truncated[: int(len(truncated) * 0.7)]
                    if len(truncated) > 2000
                    else truncated
                )
                messages = [
                    {
                        "role": "user",
                        "content": EXTRACTOR_PROMPT.format(
                            webpage_content=truncated, goal=goal
                        ),
                    }
                ]
                continue
            raw = raw.replace("``````", "").strip()
            parsed = self._safe_json_loads(raw)
            if parsed:
                return parsed
            attempt += 1
            truncated = (
                truncated[: int(len(truncated) * 0.7)]
                if len(truncated) > 2000
                else truncated
            )
            messages = [
                {
                    "role": "user",
                    "content": EXTRACTOR_PROMPT.format(
                        webpage_content=truncated, goal=goal
                    ),
                }
            ]
        return None

    def _fallback_extract(self, content: str, goal: str) -> Dict[str, str]:
        paragraphs = [para.strip() for para in content.splitlines() if para.strip()]
        keywords = [
            item.lower() for item in re.findall(r"[\w]+", goal) if len(item) > 1
        ]
        evidence_blocks: List[str] = []
        if keywords:
            for para in paragraphs:
                text_lower = para.lower()
                if any(keyword in text_lower for keyword in keywords):
                    evidence_blocks.append(para)
                if len("\n\n".join(evidence_blocks)) > 1500:
                    break
        if not evidence_blocks:
            evidence_blocks = paragraphs[:3]
        evidence_text = "\n\n".join(evidence_blocks)[:2000]
        summary_text = self._simple_summarize(evidence_blocks, goal)
        return {
            "rational": "Extracted directly from webpage due to summarizer fallback.",
            "evidence": evidence_text,
            "summary": summary_text,
        }

    def _simple_summarize(self, paragraphs: Iterable[str], goal: str) -> str:
        joined = " ".join(paragraphs)
        snippet = joined[:600]
        suffix = "..." if len(joined) > 600 else ""
        return f"Based on the captured passages related to '{goal}', key points include: {snippet}{suffix}"

    def _format_summary(self, url: str, goal: str, summary: Dict[str, str]) -> str:
        evidence = summary.get(
            "evidence", "The provided webpage content could not be accessed."
        )
        summary_text = summary.get(
            "summary", "The webpage content could not be processed."
        )
        body = (
            f"The useful information in {url} for user goal {goal} as follows: \n\n"
            f"Evidence in page: \n{evidence}\n\n"
            f"Summary: \n{summary_text}\n\n"
        )
        summary_json = json.dumps(summary, ensure_ascii=False)
        return f"{body}{EVIDENCE_JSON_START}{summary_json}{EVIDENCE_JSON_END}"

    def _build_empty_response(self, url: str, goal: str) -> str:
        summary = {
            "rational": "No accessible content retrieved; returning default summary.",
            "evidence": "",
            "summary": f"No meaningful content found for '{goal}'.",
        }
        return self._format_summary(url, goal, summary)
