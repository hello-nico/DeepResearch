from __future__ import annotations
from refactor.tongyi_ds.prompts.prompt import SYSTEM_PROMPT, EXTRACTOR_PROMPT


def load_default_system_prompt() -> str:
    if not isinstance(SYSTEM_PROMPT, str):
        raise RuntimeError("默认系统提示缺失或类型错误。")
    return SYSTEM_PROMPT


__all__ = [
    "SYSTEM_PROMPT",
    "EXTRACTOR_PROMPT",
    "load_default_system_prompt",
]
