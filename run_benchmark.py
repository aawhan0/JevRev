import json
import os
import time
from pathlib import Path

from jev_client import JevClient
from jev_router import JevRouter
from providers import OpenAICompatibleProvider
from router import KeywordRouter

DATA = Path("benchmarks/queries.jsonl")
RESULTS_DIR = Path("benchmarks/results")


def load_queries():
    return [json.loads(line) for line in DATA.read_text().splitlines() if line.strip()]


def _float_env(name: str, default: float | None = None) -> float:
    value = os.getenv(name)
    if value is None:
        if default is None:
            raise SystemExit(f"Set {name} before running this benchmark.")
        return float(default)
    return float(value)


def build_llm_provider(model: str):
    if not model:
        raise SystemExit("Set the requested LLM model environment variable.")
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
    import urllib.error

    client = JevClient()
    router = JevRouter(client)
    price = _float_env("JEV_INPUT_PRICE_PER_MTOK", 0.0)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result_path = RESULTS_DIR / "jev.json"

    existing = {}

    if result_path.exists():
        try:
            saved = json.loads(result_path.read_text())
            existing = {
                item["id"]: item
                for item in saved.get("results", [])
                if "id" in item
            }
            print(f"[Jev] Resuming with {len(existing)} saved results.")
        except (json.JSONDecodeError, KeyError, TypeError):
            print("[Jev] Existing results file is invalid; starting fresh.")

    results = list(existing.values())

    for index, row in enumerate(rows, start=1):
        if row["id"] in existing:
            print(
                f"[Jev] {index}/{len(rows)} "
                f"{row['id']} -> already saved"
            )
            continue

        max_retries = 6
        decision = None
        latency_ms = None

        for attempt in range(max_retries):
            try:
                started = time.perf_counter()
                decision = router.decide(row["query"])
                latency_ms = (time.perf_counter() - started) * 1000
                break

            except urllib.error.HTTPError as exc:
                if exc.code != 429 or attempt == max_retries - 1:
                    raise

                wait_seconds = 5 * (2 ** attempt)

                print(
                    f"[Jev] 429 on {row['id']} "
                    f"(attempt {attempt + 1}/{max_retries}), "
                    f"waiting {wait_seconds}s..."
                )

                time.sleep(wait_seconds)

        input_tokens = int(
            decision.usage.get(
                "inputTokens",
                decision.usage.get("input_tokens", 0),
            )
        )

        cost_usd = input_tokens / 1_000_000 * price

        result = {
            "id": row["id"],
            "expected": row["expected"],
            "route": decision.route,
            "confidence": decision.confidence,
            "probabilities": decision.probabilities,
            "latency_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": int(
                decision.usage.get(
                    "outputTokens",
                    decision.usage.get("output_tokens", 0),
                )
            ),
            "cost_usd": cost_usd,
        }

        results.append(result)
        existing[row["id"]] = result

        partial_summary = summarize("jev", results)

        result_path.write_text(
            json.dumps(
                {
                    "strategy": "jev",
                    "dataset": str(DATA),
                    "results": results,
                    "summary": partial_summary,
                },
                indent=2,
            )
        )

        print(
            f"[Jev] {index}/{len(rows)} "
            f"{row['id']} -> {decision.route} "
            f"confidence={decision.confidence:.2f} "
            f"({latency_ms:.0f} ms)"
        )

        if index < len(rows):
            time.sleep(3)

    return results

def run_keyword(rows):
    router = KeywordRouter()
    results = []
    for row in rows:
        decision = router.decide(row["query"])
        results.append(
            {
                "id": row["id"],
                "expected": row["expected"],
                "route": decision.route,
                "confidence": decision.confidence,
                "latency_ms": 0.0,
                "cost_usd": 0.0,
            }
        )
    return results


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
        for name in os.getenv("BENCHMARK_STRATEGIES", "jev").split(",")
        if name.strip()
    ]

    summaries = []
    for name in requested:
        if name not in strategies:
            raise SystemExit(f"Unknown strategy: {name}")
        summaries.append(summarize(name, strategies[name]()))

    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
