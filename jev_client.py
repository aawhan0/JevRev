import json
import os
from urllib.request import Request, urlopen


class JevClient:
    """Minimal HTTP adapter for the TypeSafe Jev System One API."""

    def __init__(self, api_key: str | None = None, model: str = "jev-latest"):
        self.api_key = api_key or os.getenv("TYPESAFE_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("TYPESAFE_API_KEY is required")

    def decide(self, state: str, questions: dict) -> dict:
        payload = json.dumps({
            "model": self.model,
            "state": state,
            "questions": questions,
        }).encode()

        request = Request(
            "https://api.typesafe.ai/v1/systemone",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urlopen(request, timeout=30) as response:
            return json.loads(response.read())
