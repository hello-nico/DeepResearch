"""工具函数集合。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import tiktoken


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


def parse_tool_call(content: str) -> Optional[ToolCall]:
    """解析工具调用 JSON，失败时返回 None。"""

    block = extract_tool_call_block(content)
    if not block:
        return None
    try:
        payload = json.loads(block)
    except json.JSONDecodeError:
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
