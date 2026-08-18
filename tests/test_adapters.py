from cachewise.adapters import make_client, OptimizedClient


def test_make_client_nous():
    c = make_client("nous-dsflash")
    assert isinstance(c, OptimizedClient)
    assert c.model == "deepseek-v4-flash"


def test_make_client_deepseek_direct():
    c = make_client("deepseek-direct")
    assert isinstance(c, OptimizedClient)
    assert c._use_harness is True


def test_make_client_hy3():
    c = make_client("hy3")
    assert isinstance(c, OptimizedClient)
    assert c.model == "tencent/hy3:free"


def test_unknown_env_raises():
    import pytest
    with pytest.raises(ValueError):
        make_client("no-existe")


def test_prepare_injects_stable_prefix():
    c = make_client("nous-dsflash")
    out = c._prepare([{"role": "user", "content": "Hola"}], 1.0, True)
    sys = [m for m in out if m["role"] == "system"][0]
    assert "Softgrama" in sys["content"]
    assert any(m["role"] == "user" and m["content"] == "Hola" for m in out)
