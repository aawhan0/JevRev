# JevRev

JevRev is a small research project for benchmarking **Jev-based AI routing** against simpler and LLM-based approaches.

## Goal

> Can a lightweight decision layer route requests to the cheapest capable execution path without meaningfully hurting quality?

The experiment compares:
- large LLM for every request
- small LLM for every request
- Jev-based routing with optional fallback

## Current status

- [x] Repository and benchmark fixture
- [x] Routing baseline
- [x] Metrics foundation
- [x] Provider abstraction
- [x] Jev API adapter
- [x] Live Jev benchmark runner
- [ ] Real model baselines
- [ ] Cost-normalized comparison
- [ ] Expanded evaluation dataset
- [ ] Repeated latency trials
- [ ] Final benchmark report

## Run the Jev benchmark

1. Create a TypeSafe API key.
2. Export it locally:

```bash
export TYPESAFE_API_KEY="your-key"
```

3. Run:

```bash
python run_benchmark.py
```

The script reports routing accuracy and measured end-to-end latency for the local benchmark fixture.

## Metrics

- task accuracy / quality
- latency
- estimated inference cost
- percentage of large-model calls avoided
- router decision accuracy
- fallback rate

## Research principles

This is an experiment, not a claim that Jev is universally better. Results should be measured on the same workload, with model versions and pricing assumptions documented. Negative results are valid results.

## Planned structure

```
jevrev/
├── benchmarks/
├── jev_client.py
├── jev_router.py
├── metrics.py
├── providers.py
├── router.py
├── run_benchmark.py
├── tests/
└── README.md
```

## License

MIT
