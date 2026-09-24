from dataclasses import dataclass

from jev_client import JevClient


@dataclass(frozen=True)
class JevDecision:
    route: str
    confidence: float | None
    probabilities: dict[str, float]
    usage: dict[str, int]
    market_cost_usd: float
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
        confidence = answer.get("confidence")

        gateway_metadata = (
            result.get("providerMetadata", {})
            .get("gateway", {})
        )

        market_cost = float(
            gateway_metadata.get("marketCost", 0.0)
        )

        return JevDecision(
            route=answer["choice"],
            confidence=float(confidence) if confidence is not None else None,
            probabilities={
                key: float(value)
                for key, value in answer.get("probabilities", {}).items()
            },
            usage={
                key: int(value)
                for key, value in result.get("usage", {}).items()
                if isinstance(value, (int, float))
            },
            market_cost_usd=market_cost,
            raw=answer,
        )
