"""结果载体定义。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(slots=True)
class ResultPayload:
    """LangGraph 推理的统一返回结构。"""

    content: str = ""
    evidence_chains: List[Dict[str, str]] = field(default_factory=list)
    termination: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "content": self.content,
            "evidence_chains": self.evidence_chains,
            "termination": self.termination,
        }
