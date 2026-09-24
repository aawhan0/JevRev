from dataclasses import dataclass
from statistics import mean

@dataclass(frozen=True)
class Result:
    correct: bool
    latency_ms: float
    cost_usd: float
    route: str

@dataclass(frozen=True)
class Summary:
    accuracy: float
    mean_latency_ms: float
    total_cost_usd: float
    large_calls: int
    total_calls: int

def summarize(results: list[Result]) -> Summary:
    if not results:
        return Summary(0.0, 0.0, 0.0, 0, 0)
    return Summary(
        mean(r.correct for r in results),
        mean(r.latency_ms for r in results),
        sum(r.cost_usd for r in results),
        sum(r.route == "large" for r in results),
        len(results),
    )
