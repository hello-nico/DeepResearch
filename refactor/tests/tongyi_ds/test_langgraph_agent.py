import os

import pytest

from refactor.tongyi_ds.config import AgentRuntimeConfig, GraphBuildConfig
from refactor.tongyi_ds.graph import (
    build_tongyi_deepresearch_graph,
    run_tongyi_deepresearch,
)
from refactor.tongyi_ds.result import ResultPayload
from refactor.tongyi_ds.constants import EVIDENCE_JSON_END, EVIDENCE_JSON_START
from refactor.tongyi_ds.state import build_initial_state
from refactor.tongyi_ds.tool_runtime import ToolInvoker


class DummyTool:
    def __init__(self):
        self.calls = []

    def call(self, params):
        self.calls.append(params)
        return "tool-output"


class MockLLMClient:
    def __init__(self, responses):
        self.responses = responses
        self.idx = 0

    def invoke(self, messages):
        if self.idx >= len(self.responses):
            raise AssertionError("LLM 调用次数超过预期。")
        response = self.responses[self.idx]
        self.idx += 1
        return response


@pytest.fixture()
def base_config():
    runtime = AgentRuntimeConfig(
        max_llm_calls=5, max_runtime_seconds=60, token_limit=10_000
    )
    return GraphBuildConfig(system_prompt="System:\n", agent_runtime=runtime)


def test_graph_runs_tool_flow(base_config):
    tool = DummyTool()
    tool_invoker = ToolInvoker({"search": tool})
    llm = MockLLMClient(
        [
            '<tool_call>{"name": "search", "arguments": {"query": ["langgraph"]}}</tool_call>',
            "<think>done</think>\n<answer>final answer</answer>",
        ]
    )

    graph = build_tongyi_deepresearch_graph(
        base_config, llm_client=llm, tool_invoker=tool_invoker
    )
    state = build_initial_state(
        "What is LangGraph?", base_config.system_prompt, base_config.agent_runtime
    )
    result_state = graph.invoke(state)

    assert result_state["prediction"] == "final answer"
    assert result_state["termination"] == "answer"
    assert tool.calls[0] == {"query": ["langgraph"]}


def test_graph_finishes_without_tool(base_config):
    llm = MockLLMClient(
        [
            "<think>ready</think>\n<answer>all good</answer>",
        ]
    )
    graph = build_tongyi_deepresearch_graph(
        base_config, llm_client=llm, tool_invoker=ToolInvoker({})
    )
    state = build_initial_state(
        "Ping?", base_config.system_prompt, base_config.agent_runtime
    )
    result_state = graph.invoke(state)
    assert result_state["prediction"] == "all good"
    assert result_state["termination"] == "answer"


def test_graph_exhaust_llm_calls_limits():
    runtime = AgentRuntimeConfig(
        max_llm_calls=1, max_runtime_seconds=60, token_limit=10_000
    )
    config = GraphBuildConfig(system_prompt="System:\n", agent_runtime=runtime)
    llm = MockLLMClient(["No answer yet.", "Should not be used."])
    graph = build_tongyi_deepresearch_graph(
        config, llm_client=llm, tool_invoker=ToolInvoker({})
    )
    state = build_initial_state(
        "Need answer", config.system_prompt, config.agent_runtime
    )
    result_state = graph.invoke(state)
    assert result_state["termination"] == "exhausted_llm_calls"
    assert result_state["prediction"] == ""


def test_graph_collects_evidence_chains(base_config):
    evidence_json = '{"rational": "step", "evidence": "doc", "summary": "insight"}'

    class EvidenceTool(DummyTool):
        def call(self, params):
            return (
                "summary text"
                + f"{EVIDENCE_JSON_START}{evidence_json}{EVIDENCE_JSON_END}"
            )

    tool_invoker = ToolInvoker({"visit": EvidenceTool()})
    llm = MockLLMClient(
        [
            '<tool_call>{"name": "visit", "arguments": {"url": "https://example.com", "goal": "goal"}}</tool_call>',
            "<think>ok</think>\n<answer>done</answer>",
        ]
    )
    graph = build_tongyi_deepresearch_graph(
        base_config, llm_client=llm, tool_invoker=tool_invoker
    )
    state = build_initial_state(
        "Need evidence", base_config.system_prompt, base_config.agent_runtime
    )
    result_state = graph.invoke(state)
    assert result_state["termination"] == "answer"
    assert result_state["prediction"] == "done"
    assert result_state["evidence_chains"]
    assert result_state["evidence_chains"][0]["summary"] == "insight"


@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="需要配置 OPENROUTER_API_KEY 才能执行真实推理",
)
def test_run_tongyi_deepresearch_real():
    config = GraphBuildConfig(
        tool_names=["search", "visit", "google_scholar"],
    )
    result = run_tongyi_deepresearch("A Survey on RAG", config=config)
    assert isinstance(result, ResultPayload)
    assert result.content, "真实推理应返回非空答案"
    assert result.termination, "真实推理应返回终止状态"
