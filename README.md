<p align="center">
  <img src="./assets/jevrev-logo.png" width="260" alt="JevRev" />
</p>

<p align="center"><strong>Benchmarking lightweight AI routing strategies for cost-aware model selection.</strong></p>

<p align="center">
  <a href="https://www.linkedin.com/in/aawhanvyas/">
    <img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn" />
  </a>
  <a href="https://github.com/aawhan0/JevRev">
    <img src="https://img.shields.io/github/stars/aawhan0/JevRev?style=flat-square" alt="GitHub stars" />
  </a>
  <a href="https://github.com/aawhan0/JevRev">
    <img src="https://img.shields.io/github/last-commit/aawhan0/JevRev?style=flat-square" alt="Last commit" />
  </a>
  <img src="https://img.shields.io/github/license/aawhan0/JevRev?style=flat-square" alt="MIT License" />
</p>

JevRev is a small research project for benchmarking **Jev-based AI routing** against deterministic and LLM-based approaches.

## Goal

> Can a lightweight decision layer route requests to the cheapest capable execution path without meaningfully hurting quality?

The initial experiment compares:
- a small LLM used as the router
- a large LLM used as the router
- Jev used as the router

A deterministic keyword router is also available as a non-LLM baseline.

## Current status

- [x] Repository and benchmark fixture
- [x] Routing baseline
- [x] Metrics foundation
- [x] Provider abstraction
- [x] Jev API adapter + model discovery
- [x] Unified Jev / LLM benchmark runner
- [x] Usage-based cost accounting
- [ ] Expanded evaluation dataset
- [ ] Repeated latency trials
- [ ] End-to-end execution-quality benchmark
- [ ] Final benchmark report

## Architecture

```mermaid
flowchart LR
    Q[Request] --> R[Router]
    R --> S[Small Path]
    R --> L[Large Path]
    R --> M[Metrics]
```

## Benchmark Overview

```mermaid
flowchart LR
    D[Benchmark Dataset] --> B[Benchmark Runner]
    B --> R[Routing Strategy]
    R --> E[Evaluate]
    E --> M[Metrics]
    M --> O[Results]
```

## Simple Routing Flow

```mermaid
flowchart TD
    Q[Query] --> R[Router]
    R --> D{Which path?}
    D --> S[Small]
    D --> L[Large]
    S --> X[Record Result]
    L --> X
```

## Run

Copy `.env.example` and set the credentials/configuration locally. Never commit API keys.

For Jev, set `TYPESAFE_API_KEY`. The client defaults to `jev-latest`, which is also discoverable through TypeSafe's `GET /v1/models` endpoint.

For the LLM baselines, set:
- `LLM_API_KEY`
- `LLM_API_BASE_URL`
- `SMALL_MODEL`
- `LARGE_MODEL`
- `LLM_INPUT_PRICE_PER_MTOK`
- `LLM_OUTPUT_PRICE_PER_MTOK`

Then run:

```bash
python run_benchmark.py
```

By default the runner executes `jev,small,large`. To include the deterministic baseline:

```bash
BENCHMARK_STRATEGIES=jev,small,large,keyword python run_benchmark.py
```

The runner reports **routing accuracy**, measured latency, estimated cost from reported token usage, and the number of `large` routes.

## Benchmark Results

The current 50-query benchmark produced the following results:

| Strategy | Route agreement | Mean latency | Total cost | Large routes |
|---|---:|---:|---:|---:|
| Keyword | 84% | 0 ms | $0 | 14/50 |
| Jev | 94% | ~510 ms | $0.000708 | 19/50 |
| GPT-5-mini | 100% | ~2.73 s | $0.013593 | 22/50 |

> **Note:** Route agreement is measured against hand-designed benchmark annotations, not objective ground truth. The GPT-5.5 baseline was not run because direct OpenAI API access required paid credits.

## Metrics

- route accuracy against the fixed benchmark labels
- mean measured latency
- estimated inference cost
- large-model route count
- later: end-to-end execution quality and fallback rate

## Research principles

This is an experiment, not a claim that Jev is universally better. Results must use the same workload and document model versions, pricing assumptions, and trial conditions. Do not fabricate missing measurements. Negative results are valid results.

## License

MIT
