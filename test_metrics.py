from metrics import Result, summarize

def test_summary():
    summary = summarize([
        Result(True, 10.0, 0.01, "small"),
        Result(False, 20.0, 0.10, "large"),
    ])
    assert summary.accuracy == 0.5
    assert summary.total_cost_usd == 0.11
    assert summary.large_calls == 1
