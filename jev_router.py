from dataclasses import dataclass

from jev_client import JevClient


@dataclass(frozen=True)
class JevDecision:
    route: str
    confidence: float
    raw: dict


class JevRouter:
    """Jev-backed routing decision layer."""

    def __init__(self, client: JevClient):
        self.client = client

    def decide(self, query: str) -> JevDecision:
        result = self.client.decide(
            state=query,
            questions={
                "route": {
                    "type": "choice",
                    "instructions": "Which execution path best fits this request?",
                    "criteria": {
                        "small": "A simple request that a smaller model can handle.",
                        "large": "A complex request that benefits from a stronger model.",
                    },
                }
            },
        )
        answer = result["answers"]["route"]
        return JevDecision(
            route=answer["choice"],
            confidence=float(answer["confidence"]),
            raw=answer,
        )
