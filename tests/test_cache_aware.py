from cachewise.cache_aware import build_stable_prefix, prefix_passes_cache


def test_prefix_over_threshold():
    p = build_stable_prefix("Eres Sofi de Softgrama. ")
    assert prefix_passes_cache(p) is True


def test_prefix_no_volatile_prefix():
    p = build_stable_prefix("Eres Sofi. ")
    assert p[:20].startswith("Eres Sofi.") or "[20" not in p[:20]


def test_prefix_aligned_to_block():
    p = build_stable_prefix("Politica estable de Sofi. ")
    assert prefix_passes_cache(p) is True
