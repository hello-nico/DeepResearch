import asyncio
import os
import re
import time
import json
from typing import Dict, Iterable, List, Optional, Union

import tiktoken
import requests
from openai import OpenAI
from qwen_agent.tools.base import BaseTool, register_tool

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.async_configs import BrowserConfig
from crawl4ai.processors.pdf import PDFCrawlerStrategy, PDFContentScrapingStrategy

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
        md = getattr(result.markdown, "fit_markdown", "") or getattr(result.markdown, "raw_markdown", "")
    return md or ""

# ---------------- tool ----------------
@register_tool('visit', allow_overwrite=True)
class Visit(BaseTool):
    name = 'visit'
    description = 'Visit webpage(s) and return the summary of the content.'
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": ["string", "array"],
                "items": {"type": "string"},
                "minItems": 1,
                "description": "The URL(s) of the webpage(s) to visit. Can be a single URL or an array of URLs."
            },
            "goal": {
                "type": "string",
                "description": "The goal of the visit for webpage(s)."
            }
        },
        "required": ["url", "goal"]
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
                    response_blocks.append(asyncio.run(self._read_and_summarize(item, goal)))
                except Exception as exc:
                    response_blocks.append(f"Error fetching {item}: {exc}")
            response = "\n=======\n".join(response_blocks)

        preview = response[:500] + ("..." if len(response) > 500 else "")
        print(f"[visit] Summary length {len(response)}; preview: {preview}")
        return response.strip()

    # ---------------- core with Crawl4AI ----------------
    async def _read_and_summarize(self, url: str, goal: str) -> str:
        # 1) detect PDF vs HTML
        is_pdf = is_pdf_url(url)

        # 2) build crawler
        #    downloads disabled by default; open a separate path for click-to-download flows
        browser_cfg = BrowserConfig(headless=True, verbose=False)
        text = ""
        meta: Dict = {}

        if is_pdf:
            # PDF path: use PDFCrawlerStrategy + PDFContentScrapingStrategy
            pdf_scraping = PDFContentScrapingStrategy(
                extract_images=False,
                save_images_locally=False,
                batch_size=4
            )
            pdf_strategy = PDFCrawlerStrategy()
            run_cfg = CrawlerRunConfig(scraping_strategy=pdf_scraping)

            async with AsyncWebCrawler(config=browser_cfg, crawler_strategy=pdf_strategy) as crawler:
                result = await crawler.arun(url=url, config=run_cfg)
                if not result or not result.success:
                    return self._format_summary(url, goal, self._fallback_extract("", goal))

                text = pick_markdown(result)
                meta = getattr(result, "metadata", {}) or {}
        else:
            # HTML path: default strategy
            # Keep it minimal; can customize wait_for/js_code/exclusions if needed
            run_cfg = CrawlerRunConfig(
                # example: wait_for="css:main", js_code=None
            )
            async with AsyncWebCrawler(config=browser_cfg) as crawler:
                result = await crawler.arun(url=url, config=run_cfg)
                if not result or not result.success:
                    return self._format_summary(url, goal, self._fallback_extract("", goal))

                text = pick_markdown(result)
                meta = getattr(result, "metadata", {}) or {}

        if not self._is_valid_content(text):
            return self._build_empty_response(url, goal)

        truncated = truncate_to_tokens(text, max_tokens=95000)
        summary = self._summarize_content(truncated, goal, self.call_server, int(os.getenv('VISIT_SERVER_MAX_RETRIES', 1)))
        if summary:
            return self._format_summary(url, goal, summary)

        fallback = self._fallback_extract(truncated, goal)
        return self._format_summary(url, goal, fallback)

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
            return content[left:right+1]
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

    def _summarize_content(self, content: str, goal: str, summarizer, max_retries: int) -> Optional[Dict[str, str]]:
        from prompts.prompt import EXTRACTOR_PROMPT
        prompt = EXTRACTOR_PROMPT.format(webpage_content=content, goal=goal)
        messages = [{"role": "user", "content": prompt}]
        attempt = 0
        truncated = content
        while attempt < 3:
            raw = summarizer(messages)
            if not raw:
                attempt += 1
                truncated = truncated[: int(len(truncated) * 0.7)] if len(truncated) > 2000 else truncated
                messages = [{"role": "user", "content": EXTRACTOR_PROMPT.format(webpage_content=truncated, goal=goal)}]
                continue
            raw = raw.replace("``````", "").strip()
            parsed = self._safe_json_loads(raw)
            if parsed:
                return parsed
            attempt += 1
            truncated = truncated[: int(len(truncated) * 0.7)] if len(truncated) > 2000 else truncated
            messages = [{"role": "user", "content": EXTRACTOR_PROMPT.format(webpage_content=truncated, goal=goal)}]
        return None

    def _fallback_extract(self, content: str, goal: str) -> Dict[str, str]:
        paragraphs = [para.strip() for para in content.splitlines() if para.strip()]
        keywords = [item.lower() for item in re.findall(r"[\w]+", goal) if len(item) > 1]
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
        evidence = summary.get("evidence", "The provided webpage content could not be accessed.")
        summary_text = summary.get("summary", "The webpage content could not be processed.")
        body = (
            f"The useful information in {url} for user goal {goal} as follows: \n\n"
            f"Evidence in page: \n{evidence}\n\n"
            f"Summary: \n{summary_text}\n\n"
        )
        return body
