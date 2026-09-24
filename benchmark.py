import json
from pathlib import Path
from router import KeywordRouter

DATA = Path(__file__).parent / "benchmarks" / "queries.jsonl"

def main():
    router = KeywordRouter()
    rows = [json.loads(line) for line in DATA.read_text().splitlines() if line.strip()]
    correct = sum(router.decide(row["query"]).route == row["expected"] for row in rows)
    print(f"baseline_accuracy={correct / len(rows):.2%}")

if __name__ == "__main__":
    main()
