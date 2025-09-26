"""工具执行节点。"""

from __future__ import annotations

from typing import Dict

from refactor.tongyi_ds.state import AgentState
from refactor.tongyi_ds.tool_runtime import ToolInvoker
from refactor.tongyi_ds.utils import get_logger


logger = get_logger("tool_node")


class ToolNode:
    """根据待执行的工具调用触发外部工具。"""

    def __init__(self, invoker: ToolInvoker) -> None:
        self.invoker = invoker

    def __call__(self, state: AgentState) -> AgentState:
        pending = state.get("pending_tool_call")
        if not pending:
            return AgentState()

        name = str(pending.get("name", ""))
        arguments = pending.get("arguments", {})
        if not isinstance(arguments, Dict):
            arguments = {}

        result = self.invoker.invoke(name, arguments)
        user_feedback = f"<tool_response>\n{result}\n</tool_response>"
        logger.info(user_feedback)

        return AgentState(
            messages=[{"role": "user", "content": user_feedback}],
            pending_tool_call=None,
            tool_response=result,
        )
