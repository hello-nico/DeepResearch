"""构建 Tongyi DeepResearch LangGraph 子图。"""

from __future__ import annotations

from typing import Optional

from langgraph.graph import END, StateGraph

from refactor.tongyi_ds.config import GraphBuildConfig
from refactor.tongyi_ds.finalize_node import FinalizeNode
from refactor.tongyi_ds.llm_client import LLMClient, OpenRouterLLMClient
from refactor.tongyi_ds.llm_node import LLMNode
from refactor.tongyi_ds.prompts import load_default_system_prompt
from refactor.tongyi_ds.result import ResultPayload
from refactor.tongyi_ds.state import AgentState, build_initial_state
from refactor.tongyi_ds.tool_node import ToolNode
from refactor.tongyi_ds.tool_runtime import ToolInvoker, load_default_tools


def build_tongyi_deepresearch_graph(
    config: Optional[GraphBuildConfig] = None,
    llm_client: Optional[LLMClient] = None,
    tool_invoker: Optional[ToolInvoker] = None,
):
    cfg = config or GraphBuildConfig()
    if not cfg.system_prompt:
        cfg = cfg.copy_with(system_prompt=load_default_system_prompt())

    llm = llm_client or OpenRouterLLMClient(cfg.llm_runtime, cfg.llm_generate)
    tools = tool_invoker or load_default_tools(cfg.tool_names)

    workflow = StateGraph(AgentState)
    workflow.add_node("llm", LLMNode(llm, cfg))
    workflow.add_node("tool", ToolNode(tools))
    workflow.add_node("finalize", FinalizeNode())
    workflow.set_entry_point("llm")

    def route_from_llm(state: AgentState) -> str:
        if state.get("pending_tool_call"):
            return "tool"
        if state.get("termination"):
            return "finalize"
        return "llm"

    workflow.add_conditional_edges(
        "llm",
        route_from_llm,
        {
            "tool": "tool",
            "finalize": "finalize",
            "llm": "llm",
        },
    )
    workflow.add_edge("tool", "llm")
    workflow.add_edge("finalize", END)
    return workflow.compile()


def run_tongyi_deepresearch(
    question: str,
    config: Optional[GraphBuildConfig] = None,
    llm_client: Optional[LLMClient] = None,
    tool_invoker: Optional[ToolInvoker] = None,
    extra_metadata: Optional[dict] = None,
):
    graph = build_tongyi_deepresearch_graph(config, llm_client, tool_invoker)
    cfg = config or GraphBuildConfig()
    if not cfg.system_prompt:
        cfg = cfg.copy_with(system_prompt=load_default_system_prompt())
    initial_state = build_initial_state(
        question=question,
        system_prompt=cfg.system_prompt,
        agent_runtime=cfg.agent_runtime,
        extra_metadata=extra_metadata,
    )
    recursion_limit = max(2 * cfg.agent_runtime.max_llm_calls + 10, 50)
    final_state = graph.invoke(
        initial_state,
        {"recursion_limit": recursion_limit},
    )
    termination = final_state.get("termination")
    content = final_state.get("prediction") or ""
    if termination != "answer":
        content = ""
    evidence = list(final_state.get("evidence_chains", []))
    return ResultPayload(
        content=content,
        evidence_chains=evidence,
        termination=termination,
    )
