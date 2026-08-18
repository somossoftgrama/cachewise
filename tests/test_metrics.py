from cachewise.metrics import measure, clarity_score


def test_measure_returns_fields():
    r = measure(lambda: "ok", prompt_tokens=10, completion_tokens=5)
    assert r["tps"] > 0
    assert "cost_usd" in r
    assert r["cost_usd"] > 0


def test_clarity_short_beats_verbose():
    short = "Soy Hermes, tu asistente."
    verbose = ("Bueno, pues, como tal vez sepas, soy Hermes, y en fin, "
               "para que tengas en cuenta, espero que esto ayude y no dudes "
               "en preguntar si necesitas algo más adicionalmente.")
    assert clarity_score(short) > clarity_score(verbose)


def test_clarity_empty():
    assert clarity_score("") == 0.0


def test_clarity_direct_high():
    assert clarity_score("Soy Hermes, tu asistente.") >= 0.9
