# JevRev

JevRev is a small research project for benchmarking **Jev-based AI routing** against simpler and LLM-based approaches.

## Goal

The project asks a practical systems question:

> Can a lightweight decision layer route requests to the cheapest capable execution path without meaningfully hurting quality?

The initial experiment will compare:
- large LLM for every request
- small LLM for every request
- Jev-based routing with optional fallback

## Planned metrics

- task accuracy / quality
- latency (P50 / P95)
- estimated inference cost
- percentage of large-LLM calls avoided
- router decision accuracy
- fallback rate

## Status

🚧 Initial repository setup. Benchmark implementation will be added incrementally.

## Principles

This project is an experiment, not a claim that Jev is universally better. Results should be reproducible, measured on the same workload, and reported even when a baseline performs better.

## Planned structure

```
jevrev/
├── src/
│   ├── router/
│   ├── providers/
│   └── evaluation/
├── benchmarks/
├── tests/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## License

MIT
