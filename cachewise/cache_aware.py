"""cache_aware: prefijo estable para maximizar cache hit de DeepSeek V4."""

import json
import os
import subprocess
import tempfile

from .core import estimate_tokens

CACHE_MIN_TOKENS = 1024
CACHE_BLOCK = 256


def build_stable_prefix(base: str, min_tokens: int = CACHE_MIN_TOKENS) -> str:
    """Construye un prefijo largo y estable (>= min_tokens, alineado a 256)."""
    prefix = base.strip()
    safety = 0
    while estimate_tokens(prefix) < min_tokens and safety < 200:
        prefix = (prefix + "\n" + base.strip()).strip()
        safety += 1
    tok = estimate_tokens(prefix)
    if tok % CACHE_BLOCK != 0:
        pad = CACHE_BLOCK - (tok % CACHE_BLOCK)
        prefix = prefix + "\n" + ("." * pad)
    return prefix


def prefix_passes_cache(prefix: str) -> bool:
    """True si el prefijo supera el umbral minimo de cache."""
    return estimate_tokens(prefix) >= CACHE_MIN_TOKENS


def validate_offline(prefix: str) -> dict:
    """Valida el prefijo con `dsh estimate` (gratis, sin credito)."""
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(
            [{"role": "system", "content": prefix}, {"role": "user", "content": "Hola"}],
            f,
        )
        path = f.name
    try:
        r = subprocess.run(["dsh", "estimate", path], capture_output=True, text=True, timeout=60)
        out = r.stdout + r.stderr
    finally:
        os.unlink(path)
    result = {"raw": out, "minimum_prefix_threshold": None, "cache_block_size": None,
              "estimated_hit_rate": None, "explanation": None}
    for line in out.splitlines():
        low = line.lower()
        if "minimum_prefix_threshold" in low:
            try: result["minimum_prefix_threshold"] = int(line.split(":")[-1].strip())
            except ValueError: pass
        elif "cache_block_size" in low:
            try: result["cache_block_size"] = int(line.split(":")[-1].strip())
            except ValueError: pass
        elif "estimated_hit_rate" in low:
            try: result["estimated_hit_rate"] = float(line.split(":")[-1].strip())
            except (ValueError, IndexError): pass
        elif "explanation" in low:
            result["explanation"] = line.split(":", 1)[-1].strip()
    return result
