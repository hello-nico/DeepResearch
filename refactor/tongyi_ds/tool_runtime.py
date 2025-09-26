"""工具注册与调用封装。"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Type

from refactor.tongyi_ds.tools.tool_scholar import Scholar
from refactor.tongyi_ds.tools.tool_search import Search
from refactor.tongyi_ds.tools.tool_visit import Visit


class ToolInvoker:
    """统一管理工具实例。"""

    def __init__(self, tools: Dict[str, Any]):
        self._tools = tools

    def invoke(self, name: str, arguments: Dict[str, Any]) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"Error: tool '{name}' not found."
        try:
            result = tool.call(arguments)
        except Exception as exc:  # noqa: BLE001
            return f"Error: tool '{name}' failed with {exc}."
        if isinstance(result, str):
            return result
        return str(result)

    def available(self) -> Iterable[str]:
        return self._tools.keys()


_DEFAULT_TOOLS: Dict[str, Type[Any]] = {
    "search": Search,
    "visit": Visit,
    "google_scholar": Scholar,
}


def load_default_tools(tool_names: Optional[Iterable[str]] = None) -> ToolInvoker:
    """基于当前包内工具实例化默认工具。"""

    selected = list(tool_names) if tool_names else list(_DEFAULT_TOOLS.keys())
    registry: Dict[str, Any] = {}
    for name in selected:
        tool_cls = _DEFAULT_TOOLS.get(name)
        if tool_cls is None:
            continue
        registry[name] = tool_cls()
    return ToolInvoker(registry)
