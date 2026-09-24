from dataclasses import dataclass
from typing import Literal

Route = Literal["cache", "small", "large", "fallback"]

@dataclass(frozen=True)
class Decision:
    route: Route
    confidence: float
    reason: str = ""

class KeywordRouter:
    """Simple deterministic baseline for the Jev routing benchmark."""
    def decide(self, query: str) -> Decision:
        text = query.lower()
        if any(w in text for w in ("password", "login", "account")):
            return Decision("small", 0.75, "matched simple support keywords")
        if any(w in text for w in ("architecture", "debug", "algorithm", "design")):
            return Decision("large", 0.80, "matched complex-task keywords")
        return Decision("small", 0.55, "default baseline route")
