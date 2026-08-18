"""metrics: mide t/s, costo y claridad de entrega."""

import time

PRICE_DSFLASH_IN = 0.11 / 1_000_000
PRICE_DSFLASH_OUT = 0.22 / 1_000_000

_FILLER = {"bueno", "pues", "en fin", "es decir", "por otro lado", "adicionalmente",
           "como tal vez sepas", "para que tengas en cuenta", "espero que esto ayude",
           "no dudes en preguntar", "en resumen", "básicamente", "realmente"}


def measure(fn, prompt_tokens: int, completion_tokens: int) -> dict:
    start = time.perf_counter()
    result = fn()
    elapsed = max(time.perf_counter() - start, 1e-6)
    tps = completion_tokens / elapsed
    cost = prompt_tokens * PRICE_DSFLASH_IN + completion_tokens * PRICE_DSFLASH_OUT
    return {"tps": round(tps, 2), "latency_s": round(elapsed, 4), "cost_usd": round(cost, 8), "result": result}


def clarity_score(response: str, instruction: str = "") -> float:
    if not response:
        return 0.0
    words = response.split()
    n = len(words)
    if n == 0:
        return 0.0
    length_score = 1.0 if n <= 60 else max(0.2, 60.0 / n)
    low = response.lower()
    filler_hits = sum(1 for f in _FILLER if f in low)
    filler_penalty = max(0.0, 1.0 - 0.1 * filler_hits)
    return round(min(1.0, length_score * filler_penalty), 3)
