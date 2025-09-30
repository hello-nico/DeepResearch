"""工具执行节点。"""

from __future__ import annotations

from typing import Dict

from refactor.tongyi_ds.config import AgentRuntimeConfig
from refactor.tongyi_ds.state import AgentState
from refactor.tongyi_ds.tool_runtime import ToolInvoker
from refactor.tongyi_ds.utils import get_logger


logger = get_logger("tool_node")


class ToolNode:
    """根据待执行的工具调用触发外部工具。"""

    def __init__(self, invoker: ToolInvoker, runtime: AgentRuntimeConfig) -> None:
        self.invoker = invoker
        self.runtime = runtime

    def __call__(self, state: AgentState) -> AgentState:
        pending = state.get("pending_tool_call")
        if not pending:
            return AgentState()

        name = str(pending.get("name", ""))
        arguments = pending.get("arguments", {})
        if not isinstance(arguments, Dict):
            arguments = {}

        metadata = dict(state.get("metadata", {}))
        tool_limit = max(self.runtime.max_tool_calls, 0)
        tool_calls_used = state.get("tool_calls_used", 0)

        if tool_limit and tool_calls_used >= tool_limit:
            metadata["tool_calls_remaining"] = 0
            metadata["termination_reason"] = "max_tool_calls"
            logger.info("[tool] skip executing %s: tool call limit reached", name)
            return AgentState(
                pending_tool_call=None,
                metadata=metadata,
            )

        result = self.invoker.invoke(name, arguments)
        user_feedback = f"<tool_response>\n{result}\n</tool_response>"
        logger.info(user_feedback)

        next_metadata = metadata
        next_metadata["tool_calls_remaining"] = max(
            tool_limit - (tool_calls_used + 1), 0
        )

        termination_reason = None
        if tool_limit and tool_calls_used + 1 >= tool_limit:
            termination_reason = "max_tool_calls"
            next_metadata["termination_reason"] = termination_reason
        else:
            next_metadata.pop("termination_reason", None)

        updated_state: AgentState = AgentState(
            messages=[{"role": "user", "content": user_feedback}],
            pending_tool_call=None,
            tool_response=result,
            tool_calls_used=1,
            metadata=next_metadata,
        )
        if termination_reason:
            logger.info("[tool] tool call limit reached: %s", termination_reason)
        return updated_state
