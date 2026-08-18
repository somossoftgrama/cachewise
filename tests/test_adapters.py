from cachewise.adapters import make_client, OptimizedClient


def test_make_client_nous():
    c = make_client("nous-dsflash")
    assert isinstance(c, OptimizedClient)
    assert c.model == "deepseek-v4-flash"


def test_make_client_deepseek_direct():
    c = make_client("deepseek-direct")
    assert isinstance(c, OptimizedClient)
    assert c._use_harness is True


def test_unknown_env_raises():
    import pytest
    with pytest.raises(ValueError):
        make_client("no-existe")


def test_prepare_injects_stable_prefix():
    c = make_client("nous-dsflash")
    out = c._prepare([{"role": "user", "content": "Hola"}], 1.0, True)
    sys = [m for m in out if m["role"] == "system"][0]
    # El prefijo estable debe estar presente (cache aware).
    assert "Softgrama" in sys["content"]
    # La instruccion del usuario intacta.
    assert any(m["role"] == "user" and m["content"] == "Hola" for m in out)
