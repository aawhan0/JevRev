from .models import Decision

class Router:
    """Interface for a request router."""

    def decide(self, query: str) -> Decision:
        raise NotImplementedError

class KeywordRouter(Router):
    """Deterministic baseline used before integrating Jev."""

    def decide(self, query: str) -> Decision:
        text = query.lower()
        if any(word in text for word in ("password", "login", "account")):
            return Decision("small", 0.75, "matched simple support keywords")
        if any(word in text for word in ("architecture", "debug", "algorithm", "design")):
            return Decision("large", 0.80, "matched complex-task keywords")
        return Decision("small", 0.55, "default baseline route")
