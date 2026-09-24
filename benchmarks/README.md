# Benchmark methodology

All routing strategies are evaluated on the same fixed query set.

## Dataset

The development fixture contains 50 routing cases:
- 25 simple cases labeled `small`
- 25 complex cases labeled `large`

The labels are benchmark annotations for this experiment, not ground-truth claims about any specific model.

## Metrics

- route accuracy
- mean measured latency
- estimated inference cost
- number of `large` routes
- later: end-to-end execution quality and fallback rate

## Fair comparison

Each strategy receives the exact same query text. Before publishing findings:
- pin the model identifiers
- record pricing assumptions and source dates
- run repeated trials
- report the dataset and any exclusions
- do not replace failed measurements with invented values

The current dataset is still a controlled development benchmark, not a statistically representative workload.
