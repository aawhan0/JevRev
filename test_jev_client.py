import pytest

from jev_client import JevClient


def test_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.delenv("AI_GATEWAY_API_KEY", raising=False)
    with pytest.raises(ValueError):
        JevClient()
