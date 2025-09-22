"""LangGraph 调用 Tongyi DeepResearch 作为执行器的参考示例。"""

import os
from typing import Any, List

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from inference.langgraph_executor import (
    DeepResearchAdapter,
    create_default_planner,
    create_default_synthesizer,
    create_deepresearch_executor_graph,
)
from inference.react_agent import MultiTurnReactAgent


def build_graph() -> Any:
    planner_llm = ChatOpenAI(
        model=os.environ.get("PLANNER_MODEL", "gpt-4o-mini"),
        temperature=0,
        timeout=120,
    )
    synthesizer_llm = ChatOpenAI(
        model=os.environ.get("SYNTHESIZER_MODEL", "gpt-4o-mini"),
        temperature=0.2,
        timeout=120,
    )

    planner = create_default_planner(planner_llm)
    synthesizer = create_default_synthesizer(synthesizer_llm)

    model_path = os.environ.get("DEEPRESEARCH_MODEL", "alibaba/tongyi-deepresearch-30b-a3b")
    planning_port = int(os.environ.get("DEEPRESEARCH_PORT", "6001"))
    agent = MultiTurnReactAgent(
        llm={
            "model": model_path,
            "generate_cfg": {
                "max_input_tokens": 320000,
                "max_retries": 10,
                "temperature": 0.6,
                "top_p": 0.95,
                "presence_penalty": 1.1,
            },
        },
        function_list=["search", "visit", "google_scholar", "PythonInterpreter"],
    )

    adapter = DeepResearchAdapter(
        agent=agent,
        model=model_path,
        planning_port=planning_port,
        max_rounds=int(os.environ.get("DEEPRESEARCH_MAX_ROUNDS", "8")),
        timeout_seconds=int(os.environ.get("DEEPRESEARCH_TIMEOUT", str(45 * 60))),
        max_retries=int(os.environ.get("DEEPRESEARCH_RETRIES", "2")),
    )

    return create_deepresearch_executor_graph(planner, synthesizer, adapter)


def run(question: str) -> List[str]:
    graph = build_graph()
    state = {
        "messages": [HumanMessage(content=question)],
        "task_results": [],
    }
    result = graph.invoke(state)
    return [msg.content for msg in result["messages"] if hasattr(msg, "content")]


if __name__ == "__main__":
    user_question = os.environ.get(
        "DEEPRESEARCH_QUESTION",
        "分析近一年关于 GraphRAG 的关键研究进展，并给出引用。",
    )
    outputs = run(user_question)
    print("\n".join(outputs[-2:]))
