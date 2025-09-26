"""LLM 决策节点。"""

from __future__ import annotations

import copy
import json
import time
from typing import Dict, List, Optional

from refactor.tongyi_ds.config import GraphBuildConfig
from refactor.tongyi_ds.constants import (
    EVIDENCE_JSON_END,
    EVIDENCE_JSON_START,
    EVIDENCE_REQUIRED_FIELDS,
)
from refactor.tongyi_ds.llm_client import LLMClient
from refactor.tongyi_ds.state import AgentState
from refactor.tongyi_ds.utils import (
    count_tokens,
    extract_answer,
    parse_tool_call,
    strip_tool_response,
)


class LLMNode:
    """负责与 LLM 交互，并决定后续流程。"""

    def __init__(self, llm: LLMClient, config: GraphBuildConfig) -> None:
        self.llm = llm
        self.config = config

    def __call__(self, state: AgentState) -> AgentState:
        messages: List[Dict[str, str]] = state.get("messages", [])
        metadata = copy.deepcopy(state.get("metadata", {}))
        calls_used = state.get("llm_calls_used", 0)
        round_index = state.get("round_index", calls_used)
        evidence_chains = list(state.get("evidence_chains", []))
        max_calls = self.config.agent_runtime.max_llm_calls

        if calls_used >= max_calls:
            return self._limit_reached(
                messages,
                metadata,
                reason="max_llm_calls",
                calls_used=calls_used,
                evidence_chains=evidence_chains,
            )

        start_time = metadata.get("start_time")
        runtime_budget = metadata.get("max_runtime_seconds")
        if start_time and runtime_budget and time.time() - start_time > runtime_budget:
            return self._limit_reached(
                messages,
                metadata,
                reason="timeout",
                calls_used=calls_used,
                evidence_chains=evidence_chains,
            )

        metadata["round"] = round_index + 1
        metadata["llm_calls_remaining"] = max(max_calls - (calls_used + 1), 0)

        response = self.llm.invoke(messages)
        clean_content = strip_tool_response(response)
        assistant_message = {"role": "assistant", "content": clean_content}
        print(f"[llm] round {round_index + 1}, calls_used={calls_used + 1}")

        updated_messages = messages + [assistant_message]

        token_model = metadata.get("token_model", "gpt-4o")
        token_limit = metadata.get("token_limit")
        if token_limit:
            token_count = count_tokens(updated_messages, token_model)
            metadata["token_usage"] = token_count
            print(f"[llm] token count={token_count}")
            if token_count > token_limit:
                return self._limit_reached(
                    updated_messages,
                    metadata,
                    reason="token_limit",
                    calls_used=calls_used + 1,
                    evidence_chains=evidence_chains,
                )

        tool_call = parse_tool_call(clean_content)
        pending_tool = None
        if tool_call:
            pending_tool = {"name": tool_call.name, "arguments": tool_call.arguments}

        extractor_outputs = []
        tool_response_payload = state.get("tool_response")
        if isinstance(tool_response_payload, str):
            extractor_outputs = self._extract_evidence_from_response(
                tool_response_payload
            )
            if extractor_outputs:
                evidence_chains.extend(extractor_outputs)

        answer = extract_answer(clean_content)
        termination = state.get("termination")
        prediction: Optional[str] = state.get("prediction")
        if answer:
            termination = "answer"
            prediction = answer
            pending_tool = None

        return AgentState(
            messages=[assistant_message],
            pending_tool_call=pending_tool,
            metadata=metadata,
            prediction=prediction,
            termination=termination,
            llm_calls_used=1,
            round_index=1,
            evidence_chains=evidence_chains,
            tool_response=None,
        )

    def _limit_reached(
        self,
        messages: List[Dict[str, str]],
        metadata: Dict[str, object],
        reason: str,
        calls_used: int,
        evidence_chains: List[Dict[str, str]],
    ) -> AgentState:
        termination_reason = {
            "max_llm_calls": "exhausted_llm_calls",
            "timeout": "timeout",
            "token_limit": "token_limit_reached",
        }.get(reason, reason)
        max_calls = self.config.agent_runtime.max_llm_calls
        metadata["round"] = calls_used
        metadata["llm_calls_remaining"] = max(max_calls - calls_used, 0)
        prediction = "No answer found."
        if reason == "max_llm_calls":
            prediction = "No answer found: maximum LLM call limit reached."
        elif reason == "timeout":
            prediction = f"No answer found after {metadata.get('max_runtime_seconds', 0) / 60:.1f} mins"
        elif reason == "token_limit":
            prediction = "Token limit exceeded before producing a final answer."
        metadata["termination_reason"] = reason
        return AgentState(
            prediction=prediction,
            termination=termination_reason,
            metadata=metadata,
            evidence_chains=evidence_chains,
            tool_response=None,
            llm_calls_used=calls_used,
            round_index=calls_used,
        )

    def _extract_evidence_from_response(self, payload: str) -> List[Dict[str, str]]:
        records: List[Dict[str, str]] = []
        cursor = 0
        while True:
            start = payload.find(EVIDENCE_JSON_START, cursor)
            if start == -1:
                break
            end = payload.find(EVIDENCE_JSON_END, start)
            if end == -1:
                break
            json_segment = payload[start + len(EVIDENCE_JSON_START) : end].strip()
            parsed = self._safe_json_loads(json_segment)
            if parsed:
                records.append(parsed)
            cursor = end + len(EVIDENCE_JSON_END)
        return records

    def _safe_json_loads(self, payload: str) -> Optional[Dict[str, str]]:
        if not payload:
            return None
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        if not EVIDENCE_REQUIRED_FIELDS.issubset(data.keys()):
            return None
        return {
            "rational": str(data.get("rational", "")),
            "evidence": str(data.get("evidence", "")),
            "summary": str(data.get("summary", "")),
        }
