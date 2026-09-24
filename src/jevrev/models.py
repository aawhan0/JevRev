from dataclasses import dataclass
from typing import Literal

Route = Literal["cache", "small", "large", "fallback"]

@dataclass(frozen=True)
class Decision:
    route: Route
    confidence: float
    reason: str = ""
