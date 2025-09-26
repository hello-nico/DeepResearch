"""收束节点，用于补全终止状态。"""

from __future__ import annotations

from refactor.tongyi_ds.state import AgentState


class FinalizeNode:
    def __call__(self, state: AgentState) -> AgentState:
        prediction = state.get("prediction") or ""
        termination = state.get("termination") or "no_answer"
        evidence = list(state.get("evidence_chains", []))
        llm_calls_used = state.get("llm_calls_used", 0)
        round_index = state.get("round_index", llm_calls_used)
        metadata = state.get("metadata", {})
        tool_response = None
        if termination != "answer":
            prediction = ""
        return AgentState(
            prediction=prediction,
            termination=termination,
            evidence_chains=evidence,
            llm_calls_used=llm_calls_used,
            round_index=round_index,
            metadata=metadata,
            tool_response=tool_response,
        )
