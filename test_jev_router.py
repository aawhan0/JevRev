from jev_router import JevRouter


class FakeClient:
    def decide(self, state, questions):
        return {
            "answers": {
                "route": {
                    "type": "choice",
                    "choice": "large",
                    "confidence": 0.91,
                    "probabilities": {"small": 0.09, "large": 0.91},
                }
            },
            "usage": {"input_tokens": 100, "output_tokens": 1},
        }


def test_jev_router_preserves_choice_and_usage():
    decision = JevRouter(FakeClient()).decide("design a distributed scheduler")

    assert decision.route == "large"
    assert decision.confidence == 0.91
    assert decision.probabilities["large"] == 0.91
    assert decision.usage["input_tokens"] == 100
