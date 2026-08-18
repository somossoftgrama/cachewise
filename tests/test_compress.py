from cachewise.compress import compress_history
from cachewise.core import estimate_tokens


def _total(messages):
    return sum(estimate_tokens(m.get("content", "")) for m in messages)


def test_reduces_tokens():
    hist = [{"role": "user", "content": "x"},
            {"role": "tool", "content": "BIG " * 500},
            {"role": "user", "content": "resume?"}]
    out = compress_history(hist, fidelity=0.5)
    assert _total(out) < _total(hist)


def test_keeps_active_instruction():
    hist = [{"role": "user", "content": "x"},
            {"role": "tool", "content": "BIG " * 500},
            {"role": "user", "content": "resume?"}]
    out = compress_history(hist, fidelity=0.5)
    assert any(m["role"] == "user" and "resume?" in m["content"] for m in out)


def test_no_degrade_by_default():
    hist = [{"role": "user", "content": "instruccion unica"}]
    out = compress_history(hist, fidelity=0.0)
    assert any(m["role"] == "user" and "instruccion unica" in m["content"] for m in out)


def test_fidelity_one_keeps_all():
    hist = [{"role": "user", "content": "x"},
            {"role": "tool", "content": "BIG " * 500}]
    out = compress_history(hist, fidelity=1.0)
    assert _total(out) == _total(hist)
