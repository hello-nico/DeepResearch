"""工具函数集合。"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import json5
import tiktoken

from refactor.tongyi_ds.constants import EVIDENCE_JSON_END, EVIDENCE_JSON_START


@dataclass(slots=True)
class ToolCall:
    name: str
    arguments: Dict[str, Any]


def count_tokens(messages: List[Dict[str, str]], model: str) -> int:
    """统计消息序列消耗的 token 数量。"""

    try:
        tokenizer = tiktoken.encoding_for_model(model)
    except Exception:  # noqa: BLE001
        tokenizer = tiktoken.get_encoding("cl100k_base")

    total = 0
    for msg in messages:
        content = msg.get("content", "")
        role = msg.get("role", "")
        total += len(tokenizer.encode(content))
        total += len(tokenizer.encode(role)) + 4
    return total


def strip_tool_response(content: str) -> str:
    """截去模型回答中的 <tool_response> 块，保留可读部分。"""

    if "<tool_response>" not in content:
        return content.strip()
    return content.split("<tool_response>", 1)[0].strip()


def extract_tool_call_block(content: str) -> Optional[str]:
    """提取 <tool_call>...</tool_call> 中的原始 JSON 文本。"""

    pattern = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL)
    match = pattern.search(content)
    if not match:
        return None
    return match.group(1).strip()


JSON5_DECODE_ERROR = getattr(json5, "JSONDecodeError", Exception)

_LOGGER_ROOT_NAME = "tongyi_ds"


def _ensure_logger_configured() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_ROOT_NAME)
    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def get_logger(child: Optional[str] = None) -> logging.Logger:
    base = _ensure_logger_configured()
    if not child:
        return base
    return base.getChild(child)


def build_evidence_block(
    summary: str,
    evidence: str,
    rational: str = "",
    url: str = "",
) -> str:
    """生成带有证据链标记的 JSON 片段，附加可选 URL。"""

    record = {
        "rational": rational,
        "evidence": evidence,
        "summary": summary,
    }
    url_value = url.strip()
    if url_value:
        record["url"] = url_value
    payload = json.dumps(record, ensure_ascii=False)
    return f"{EVIDENCE_JSON_START}{payload}{EVIDENCE_JSON_END}"


def parse_tool_call(content: str) -> Optional[ToolCall]:
    """解析工具调用 JSON，失败时返回 None。"""

    block = extract_tool_call_block(content)
    if not block:
        return None
    try:
        payload = json5.loads(block)
    except JSON5_DECODE_ERROR:
        return None
    name = payload.get("name")
    arguments = payload.get("arguments", {})
    if not isinstance(name, str):
        return None
    if not isinstance(arguments, dict):
        return None
    return ToolCall(name=name, arguments=arguments)


def extract_answer(content: str) -> Optional[str]:
    """获取 <answer>...</answer> 结构内的最终答案。"""

    if "<answer>" not in content:
        return None
    start = content.find("<answer>") + len("<answer>")
    end = content.find("</answer>", start)
    if end == -1:
        return None
    return content[start:end].strip()
