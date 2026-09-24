from router import KeywordRouter


def test_simple_support_query_routes_to_small():
    assert KeywordRouter().decide("I forgot my account password").route == "small"


def test_complex_architecture_query_routes_to_large():
    assert KeywordRouter().decide("How would you design a distributed architecture?").route == "large"
