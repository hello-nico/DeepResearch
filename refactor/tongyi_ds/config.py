"""LangGraph 构建所需的配置对象。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(slots=True)
class LLMGenerateConfig:
    """控制 OpenAI 兼容接口的生成参数。"""

    temperature: float = 0.6
    top_p: float = 0.95
    presence_penalty: float = 1.1
    max_tokens: int = 10_000
    logprobs: bool = True


@dataclass(slots=True)
class LLMRuntimeConfig:
    """LLM 调用相关的运行时设置。"""

    model: str = "alibaba/tongyi-deepresearch-30b-a3b"
    base_url: str = field(
        default_factory=lambda: os.getenv(
            "OPENROUTER_API_BASE", "https://openrouter.ai/api/v1"
        )
    )
    api_key_env_var: str = "OPENROUTER_API_KEY"
    timeout_seconds: float = 600.0
    stop_sequences: List[str] = field(
        default_factory=lambda: ["\n<tool_response>", "<tool_response>"]
    )
    max_retries: int = 10
    reasoning_prefix: str = "<think>\n"
    reasoning_suffix: str = "\n</think>"


@dataclass(slots=True)
class AgentRuntimeConfig:
    """Agent 内部控制参数。"""

    max_llm_calls: int = int(os.getenv("MAX_LLM_CALL_PER_RUN", "100"))
    max_runtime_seconds: int = 150 * 60
    token_limit: int = 108 * 1024
    token_model: str = "gpt-4o"


@dataclass(slots=True)
class GraphBuildConfig:
    """LangGraph 子图构建所需的完整配置。"""

    system_prompt: str = ""
    llm_generate: LLMGenerateConfig = field(default_factory=LLMGenerateConfig)
    llm_runtime: LLMRuntimeConfig = field(default_factory=LLMRuntimeConfig)
    agent_runtime: AgentRuntimeConfig = field(default_factory=AgentRuntimeConfig)
    tool_names: Optional[List[str]] = None

    def copy_with(self, **kwargs) -> "GraphBuildConfig":
        data = {
            "system_prompt": self.system_prompt,
            "llm_generate": self.llm_generate,
            "llm_runtime": self.llm_runtime,
            "agent_runtime": self.agent_runtime,
            "tool_names": self.tool_names,
        }
        data.update(kwargs)
        return GraphBuildConfig(**data)
