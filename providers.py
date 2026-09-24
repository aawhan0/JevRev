import json
import time
from dataclasses import dataclass
from typing import Protocol
from urllib.request import Request, urlopen


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


class OpenAICompatibleProvider:
    """Minimal Chat Completions-compatible provider for real baselines.

    The model is instructed to return only 'small' or 'large'. Pricing is
    supplied by the caller so benchmark code never invents provider prices.
    """

    def __init__(
        self,
        *,
        endpoint: str,
        api_key: str,
        model: str,
        input_price_per_mtok: float,
        output_price_per_mtok: float,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.input_price_per_mtok = input_price_per_mtok
        self.output_price_per_mtok = output_price_per_mtok

    def generate(self, prompt: str) -> ModelResponse:
        body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return exactly one word: small or large. "
                        "Choose small for simple requests and large for requests "
                        "that require substantially stronger reasoning."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }

        request = Request(
            f"{self.endpoint}/chat/completions",
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        started = time.perf_counter()

        with urlopen(request, timeout=60) as response:
            payload = json.loads(response.read())

        latency_ms = (time.perf_counter() - started) * 1000

        text = payload["choices"][0]["message"]["content"].strip().lower()

        usage = payload.get("usage", {})
        input_tokens = int(usage.get("prompt_tokens", 0))
        output_tokens = int(usage.get("completion_tokens", 0))

        gateway_cost = usage.get("cost")

        if gateway_cost is not None:
            cost_usd = float(gateway_cost)
        else:
            cost_usd = (
                input_tokens / 1_000_000 * self.input_price_per_mtok
                + output_tokens / 1_000_000 * self.output_price_per_mtok
            )

        return ModelResponse(
            text=text,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
        )
