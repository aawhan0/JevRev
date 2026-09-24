from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelResponse:
    text: str
    latency_ms: float
    cost_usd: float


class Provider(Protocol):
    def generate(self, prompt: str) -> ModelResponse:
        ...


class MockProvider:
    """Deterministic provider for local benchmark development."""

    def __init__(self, name: str, latency_ms: float, cost_usd: float):
        self.name = name
        self.latency_ms = latency_ms
        self.cost_usd = cost_usd

    def generate(self, prompt: str) -> ModelResponse:
        return ModelResponse(
            text=f"[{self.name}] response for: {prompt}",
            latency_ms=self.latency_ms,
            cost_usd=self.cost_usd,
        )
