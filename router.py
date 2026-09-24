from dataclasses import dataclass
from typing import Literal, Protocol

Route = Literal["cache", "small", "large", "fallback"]


@dataclass(frozen=True)
class Decision:
    route: Route
    confidence: float
    reason: str = ""


class Provider(Protocol):
    def generate(self, query: str): ...


class KeywordRouter:
    """Deterministic routing baseline.

    This is the decision boundary that a Jev-backed router can replace
    without changing the downstream provider layer.
    """

    def decide(self, query: str) -> Decision:
        text = query.lower()
        if any(w in text for w in ("password", "login", "account")):
            return Decision("small", 0.75, "matched simple support keywords")
        if any(w in text for w in ("architecture", "debug", "algorithm", "design")):
            return Decision("large", 0.80, "matched complex-task keywords")
        return Decision("small", 0.55, "default baseline route")


class CostAwareRouter:
    def __init__(self, small: Provider, large: Provider):
        self.small = small
        self.large = large

    def generate(self, query: str):
        decision = KeywordRouter().decide(query)
        provider = self.large if decision.route == "large" else self.small
        return decision, provider.generate(query)
