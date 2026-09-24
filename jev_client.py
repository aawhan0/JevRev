import json
import os
from urllib.request import Request, urlopen


class JevClient:
    """Minimal HTTP adapter for Jev through Vercel AI Gateway."""

    endpoint = "https://ai-gateway.vercel.sh/v1/evaluate"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or os.getenv("AI_GATEWAY_API_KEY")
        self.model = model or os.getenv("JEV_MODEL", "typesafe-ai/jev")
        if not self.api_key:
            raise ValueError("AI_GATEWAY_API_KEY is required")

    def decide(self, state: str, questions: dict) -> dict:
        payload = json.dumps(
            {
                "model": self.model,
                "state": state,
                "questions": questions,
            }
        ).encode()

        request = Request(
            self.endpoint,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urlopen(request, timeout=30) as response:
            return json.loads(response.read())
