from cachewise.core import estimate_tokens


def test_estimate_tokens_basic():
    assert estimate_tokens("Hola mundo") >= 2


def test_estimate_tokens_long():
    assert estimate_tokens("x" * 4000) >= 900


def test_estimate_tokens_empty():
    assert estimate_tokens("") == 0
