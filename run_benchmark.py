import json
import os
import time
from pathlib import Path

from jev_client import JevClient
from jev_router import JevRouter
from providers import OpenAICompatibleProvider
from router import KeywordRouter

DATA = Path("benchmarks/queries.jsonl")


def load_queries():
    return [json.loads(line) for line in DATA.read_text().splitlines() if line.strip()]


def _float_env(name: str, default: float | None = None) -> float:
    value = os.getenv(name)
    if value is None:
        if default is None:
            raise SystemExit(f"Set {name} before running this benchmark.")
        return default
    return float(value)


def build_llm_provider(model: str):
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE_URL")
    if not api_key or not base_url:
        raise SystemExit("Set LLM_API_KEY and LLM_API_BASE_URL for LLM baselines.")
    return OpenAICompatibleProvider(
        endpoint=base_url,
        api_key=api_key,
        model=model,
        input_price_per_mtok=_float_env("LLM_INPUT_PRICE_PER_MTOK"),
        output_price_per_mtok=_float_env("LLM_OUTPUT_PRICE_PER_MTOK"),
    )


def run_jev(rows):
    client = JevClient()
    router = JevRouter(client)
    price = _float_env("TYPESAFE_INPUT_PRICE_PER_MTOK", 0.042)
    results = []

    for row in rows:
        started = time.perf_counter()
        decision = router.decide(row["query"])
        latency_ms = (time.perf_counter() - started) * 1000
        usage = decision.raw.get("_usage", {})
        input_tokens = int(usage.get("input_tokens", 0))
        cost_usd = input_tokens / 1_000_000 * price
        results.append(
            {
                "id": row["id"],
                "expected": row["expected"],
                "route": decision.route,
                "confidence": decision.confidence,
                "latency_ms": latency_ms,
                "cost_usd": cost_usd,
            }
        )
    return results


def run_keyword(rows):
    router = KeywordRouter()
    return [
        {
            "id": row["id"],
            "expected": row["expected"],
            "route": router.decide(row["query"]).route,
            "confidence": router.decide(row["query"]).confidence,
            "latency_ms": 0.0,
            "cost_usd": 0.0,
        }
        for row in rows
    ]


def run_llm(rows, model: str):
    provider = build_llm_provider(model)
    results = []
    for row in rows:
        response = provider.generate(row["query"])
        results.append(
            {
                "id": row["id"],
                "expected": row["expected"],
                "route": response.text,
                "confidence": None,
                "latency_ms": response.latency_ms,
                "cost_usd": response.cost_usd,
            }
        )
    return results


def summarize(strategy, results):
    total = len(results)
    correct = sum(r["route"] == r["expected"] for r in results)
    return {
        "strategy": strategy,
        "dataset": str(DATA),
        "total_queries": total,
        "route_accuracy": correct / total if total else 0.0,
        "mean_latency_ms": (
            sum(r["latency_ms"] for r in results) / total if total else 0.0
        ),
        "total_cost_usd": sum(r["cost_usd"] for r in results),
        "large_calls": sum(r["route"] == "large" for r in results),
    }


def main():
    rows = load_queries()
    strategies = {
        "jev": lambda: run_jev(rows),
        "small": lambda: run_llm(rows, os.getenv("SMALL_MODEL", "")),
        "large": lambda: run_llm(rows, os.getenv("LARGE_MODEL", "")),
        "keyword": lambda: run_keyword(rows),
    }

    requested = [
        name.strip()
        for name in os.getenv("BENCHMARK_STRATEGIES", "jev,small,large").split(",")
        if name.strip()
    ]

    summaries = []
    for name in requested:
        if name not in strategies:
            raise SystemExit(f"Unknown strategy: {name}")
        if name in {"small", "large"} and not strategies[name]:
            raise SystemExit(f"Missing configuration for {name}")
        summaries.append(summarize(name, strategies[name]()))

    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
