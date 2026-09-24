import json
import os
import time
from pathlib import Path

from jev_client import JevClient


DATA = Path("benchmarks/queries.jsonl")


def load_queries():
    return [json.loads(line) for line in DATA.read_text().splitlines() if line.strip()]


def main():
    if not os.getenv("TYPESAFE_API_KEY"):
        raise SystemExit("Set TYPESAFE_API_KEY before running the live Jev benchmark.")

    client = JevClient()
    rows = load_queries()
    correct = 0
    total_latency = 0.0

    for row in rows:
        start = time.perf_counter()
        result = client.decide(
            state=row["query"],
            questions={
                "route": {
                    "type": "choice",
                    "instructions": "Choose the best execution path.",
                    "criteria": {
                        "small": "A smaller model is sufficient.",
                        "large": "A larger model is justified by task complexity.",
                    },
                }
            },
        )
        elapsed = (time.perf_counter() - start) * 1000
        answer = result["answers"]["route"]
        route = answer["choice"]
        correct += route == row["expected"]
        total_latency += elapsed
        print(f'{row["id"]}: route={route} confidence={answer.get("confidence")} latency_ms={elapsed:.1f}')

    print(f"accuracy={correct / len(rows):.2%}")
    print(f"mean_latency_ms={total_latency / len(rows):.1f}")


if __name__ == "__main__":
    main()
