from cachewise.prethinker import prethinker_directive, apply_prethinker


def test_directive_has_laconic_keyword():
    d = prethinker_directive()
    assert ("lacónico" in d.lower()) or ("concis" in d.lower())


def test_apply_injects_into_system():
    msgs = [{"role": "system", "content": "Eres Sofi."},
            {"role": "user", "content": "¿Quién eres?"}]
    out = apply_prethinker(msgs)
    sys = [m for m in out if m["role"] == "system"][0]
    assert "lacónico" in sys["content"]


def test_apply_keeps_user_instruction():
    msgs = [{"role": "system", "content": "Eres Sofi."},
            {"role": "user", "content": "¿Quién eres?"}]
    out = apply_prethinker(msgs)
    user = [m for m in out if m["role"] == "user"][0]
    assert user["content"] == "¿Quién eres?"


def test_apply_creates_system_if_missing():
    msgs = [{"role": "user", "content": "Hola"}]
    out = apply_prethinker(msgs)
    assert any(m["role"] == "system" for m in out)
    assert out[0]["role"] == "system"
