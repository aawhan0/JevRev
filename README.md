# JevRev

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
flowchart TD
    Q[Benchmark Query] --> R{Routing Strategy}

    R -->|keyword| K[Deterministic Keyword Router]
    R -->|jev| J[JevRouter]
    R -->|small| S[LLM Router]
    R -->|large| L[LLM Router]

    J --> JC[JevClient]
    JC --> G[Vercel AI Gateway]
    G --> JV[Jev Decision]

    S --> P[Provider Adapter]
    L --> P
    P --> G2[OpenAI-Compatible Gateway]

    K --> D[Route Decision]
    JV --> D
    S --> D
    L --> D

    D --> M[Benchmark Metrics]
    M --> O[Persisted JSON Results]
```

## Benchmark Flow

```mermaid
flowchart LR
    A[queries.jsonl<br/>50 queries] --> B[Benchmark Runner]
    B --> C1[Jev]
    B --> C2[GPT-5-mini]
    B --> C3[Keyword]

    C1 --> D[Route Decision]
    C2 --> D
    C3 --> D

    D --> E[Compare with<br/>hand-designed label]
    E --> F[Accuracy]
    D --> G[Latency]
    D --> H[Cost]
    D --> I[Large-route count]

    F --> J[benchmarks/results/*.json]
    G --> J
    H --> J
    I --> J
```

## Routing Decision

```mermaid
sequenceDiagram
    participant Q as Query
    participant R as Router
    participant J as Jev
    participant M as Model Path
    participant X as Metrics

    Q->>R: classify request
    alt Jev strategy
        R->>J: evaluate route
        J-->>R: small / large + confidence
    else LLM strategy
        R->>M: classify with LLM
        M-->>R: small / large
    else Keyword strategy
        R->>R: apply keyword rules
    end
    R->>X: record route, latency, cost
    X->>X: compare with annotation
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
