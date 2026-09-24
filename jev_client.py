import json
import os
from urllib.request import Request, urlopen


class JevClient:
    """Minimal HTTP adapter for the TypeSafe Jev System One API."""

    endpoint = "https://api.typesafe.ai/v1/systemone"
    models_endpoint = "https://api.typesafe.ai/v1/models"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("TYPESAFE_API_KEY")
        self.model = model or os.getenv("TYPESAFE_MODEL", "jev-latest")
        if not self.api_key:
            raise ValueError("TYPESAFE_API_KEY is required")

    def _request(self, url: str, method: str = "GET", payload: dict | None = None) -> dict:
        data = json.dumps(payload).encode() if payload is not None else None
        request = Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read())

    def list_models(self) -> list[dict]:
        """Return models available to the authenticated account."""
        return self._request(self.models_endpoint)["models"]

    def decide(self, state: str, questions: dict) -> dict:
        return self._request(
            self.endpoint,
            method="POST",
            payload={
                "model": self.model,
                "state": state,
                "questions": questions,
            },
        )
