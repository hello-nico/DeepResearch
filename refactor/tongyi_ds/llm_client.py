"""OpenRouter LLM 封装。"""

from __future__ import annotations

import os
import random
import time
from typing import List, Protocol

from openai import APIConnectionError, APIError, APITimeoutError, OpenAI

from refactor.tongyi_ds.config import LLMGenerateConfig, LLMRuntimeConfig


class LLMClient(Protocol):
    """最简 LLM 调用协议，便于测试替换。"""

    def invoke(self, messages: List[dict]) -> str:  # pragma: no cover - 协议定义
        ...


class OpenRouterLLMClient:
    """兼容 OpenRouter OpenAI 接口的调用实现。"""

    def __init__(
        self,
        runtime: LLMRuntimeConfig,
        generate: LLMGenerateConfig,
    ) -> None:
        self.runtime = runtime
        self.generate = generate
        self._client: OpenAI | None = None

    def invoke(self, messages: List[dict]) -> str:
        client = self._ensure_client()
        base_sleep = 1.0

        for attempt in range(self.runtime.max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.runtime.model,
                    messages=messages,
                    stop=self.runtime.stop_sequences,
                    temperature=self.generate.temperature,
                    top_p=self.generate.top_p,
                    presence_penalty=self.generate.presence_penalty,
                    max_tokens=self.generate.max_tokens,
                    logprobs=self.generate.logprobs,
                )
                choice = response.choices[0]
                reasoning = getattr(choice.message, "reasoning", None)
                content = choice.message.content or ""
                if reasoning:
                    combined = (
                        f"{self.runtime.reasoning_prefix}{reasoning.strip()}{self.runtime.reasoning_suffix}\n"
                        f"{content}"
                    )
                    return combined.strip()
                return content.strip()
            except (APIError, APIConnectionError, APITimeoutError) as exc:
                if attempt == self.runtime.max_retries - 1:
                    raise RuntimeError(f"OpenRouter 调用失败: {exc}") from exc
                sleep_time = min(base_sleep * (2**attempt) + random.uniform(0, 1), 30)
                time.sleep(sleep_time)
            except Exception as exc:  # noqa: BLE001
                if attempt == self.runtime.max_retries - 1:
                    raise RuntimeError(f"LLM 调用出现未知错误: {exc}") from exc
                sleep_time = min(base_sleep * (2**attempt) + random.uniform(0, 1), 30)
                time.sleep(sleep_time)

        raise RuntimeError("OpenRouter 调用在所有重试后仍失败。")

    def _ensure_client(self) -> OpenAI:
        if self._client is not None:
            return self._client
        api_key = os.getenv(self.runtime.api_key_env_var)
        if not api_key:
            raise RuntimeError(
                f"未找到 {self.runtime.api_key_env_var} 环境变量，无法调用 OpenRouter。"
            )
        self._client = OpenAI(
            api_key=api_key,
            base_url=self.runtime.base_url,
            timeout=self.runtime.timeout_seconds,
        )
        return self._client
