import http.client
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Union

import json5
from qwen_agent.tools.base import BaseTool, register_tool

from refactor.tongyi_ds.utils import build_evidence_block, get_logger


SERPER_KEY = os.environ.get("SERPER_KEY_ID")
JSON5_DECODE_ERROR = getattr(json5, "JSONDecodeError", Exception)
logger = get_logger("tool_scholar")


@register_tool("google_scholar", allow_overwrite=True)
class Scholar(BaseTool):
    name = "google_scholar"
    description = "Leverage Google Scholar to retrieve relevant information from academic publications. Accepts multiple queries."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "array",
                "items": {"type": "string", "description": "The search query."},
                "minItems": 1,
                "description": "The list of search queries for Google Scholar.",
            },
        },
        "required": ["query"],
    }

    def google_scholar_with_serp(self, query: str):
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps(
            {
                "q": query,
            }
        )
        headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
        for i in range(5):
            try:
                conn.request("POST", "/scholar", payload, headers)
                res = conn.getresponse()
                break
            except Exception as exc:
                logger.exception("[scholar] request failure for %s: %s", query, exc)
                if i == 4:
                    return (
                        "Google Scholar Timeout, return None, Please try again later."
                    )
                continue

        data = res.read()

        try:
            results = json5.loads(data.decode("utf-8"))
        except JSON5_DECODE_ERROR:
            return "Google Scholar response could not be decoded."
        try:
            if "organic" not in results:
                raise Exception(
                    f"No results found for query: '{query}'. Use a less specific query."
                )

            web_snippets = list()
            evidence_blocks: List[str] = []
            idx = 0
            if "organic" in results:
                for page in results["organic"]:
                    idx += 1
                    date_published = ""
                    if "year" in page:
                        date_published = "\nDate published: " + str(page["year"])

                    publicationInfo = ""
                    if "publicationInfo" in page:
                        publicationInfo = (
                            "\npublicationInfo: " + page["publicationInfo"]
                        )

                    snippet = ""
                    if "snippet" in page:
                        snippet = "\n" + page["snippet"]

                    link_info = "no available link"
                    if "pdfUrl" in page:
                        link_info = "pdfUrl: " + page["pdfUrl"]

                    citedBy = ""
                    if "citedBy" in page:
                        citedBy = "\ncitedBy: " + str(page["citedBy"])

                    redacted_version = f"{idx}. [{page['title']}]({link_info}){publicationInfo}{date_published}{citedBy}\n{snippet}"

                    redacted_version = redacted_version.replace(
                        "Your browser can't play this video.", ""
                    )
                    web_snippets.append(redacted_version)

                    snippet_text = page.get("snippet", "")
                    evidence_blocks.append(
                        build_evidence_block(
                            summary=(snippet_text or page.get("title", "")).strip(),
                            evidence=(snippet_text or page.get("title", "")).strip(),
                            rational=f"Scholar result {idx} for query '{query}'.",
                            url=str(
                                page.get("link")
                                or page.get("pdfUrl")
                                or page.get("cachedPageUrl")
                                or ""
                            ),
                        )
                    )

            content = (
                f"A Google scholar for '{query}' found {len(web_snippets)} results:\n\n## Scholar Results\n"
                + "\n\n".join(web_snippets)
            )
            evidence_section = "\n".join(block for block in evidence_blocks if block)
            return f"{content}\n{evidence_section}" if evidence_section else content
        except Exception:
            return f"No results found for '{query}'. Try with a more general query."

    def call(self, params: Union[str, dict], **kwargs) -> str:
        # assert GOOGLE_SEARCH_KEY is not None, "Please set the IDEALAB_SEARCH_KEY environment variable."
        try:
            params = self._verify_json_format_args(params)
            query = params["query"]
        except Exception:
            return "[google_scholar] Invalid request format: Input must be a JSON object containing 'query' field"

        if isinstance(query, str):
            response = self.google_scholar_with_serp(query)
        else:
            assert isinstance(query, List)
            with ThreadPoolExecutor(max_workers=3) as executor:

                response = list(executor.map(self.google_scholar_with_serp, query))
            response = "\n=======\n".join(response)
        return response
