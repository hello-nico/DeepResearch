"""Agent 状态定义与初始状态构造。"""

from __future__ import annotations

import operator
import time
from datetime import date
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from refactor.tongyi_ds.config import AgentRuntimeConfig


class AgentState(TypedDict, total=False):
    """LangGraph 节点间传递的统一状态。"""

    messages: Annotated[List[Dict[str, str]], operator.add]
    llm_calls_used: Annotated[int, operator.add]
    round_index: Annotated[int, operator.add]
    evidence_chains: Annotated[List[Dict[str, str]], operator.add]
    pending_tool_call: Optional[Dict[str, Any]]
    tool_response: Optional[str]
    prediction: Optional[str]
    termination: Optional[str]
    metadata: Dict[str, Any]


def build_initial_state(
    question: str,
    system_prompt: str,
    agent_runtime: Optional[AgentRuntimeConfig] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> AgentState:
    """构造 LangGraph 所需的初始状态。"""

    runtime = agent_runtime or AgentRuntimeConfig()
    today = date.today().strftime("%Y-%m-%d")
    sys_content = f"{system_prompt}{today}" if system_prompt else today

    metadata: Dict[str, Any] = {
        "round": 0,
        "llm_calls_remaining": runtime.max_llm_calls,
        "start_time": time.time(),
        "max_runtime_seconds": runtime.max_runtime_seconds,
        "token_limit": runtime.token_limit,
        "token_model": runtime.token_model,
    }
    if extra_metadata:
        metadata.update(extra_metadata)

    initial_messages: List[Dict[str, str]] = [
        {"role": "system", "content": sys_content},
        {"role": "user", "content": question},
    ]

    return AgentState(
        messages=initial_messages,
        llm_calls_used=0,
        round_index=0,
        evidence_chains=[],
        pending_tool_call=None,
        tool_response=None,
        prediction=None,
        termination=None,
        metadata=metadata,
    )
