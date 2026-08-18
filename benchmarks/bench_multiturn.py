"""Test multi-turno real: misma conversacion acumulada, mide cache hit real.

DeepSeek expone en usage: prompt_cache_hit_tokens, prompt_cache_miss_tokens
y cache_hit_rate (campos del harness). Esto es la VERDAD del proveedor, no
una estimacion offline.
"""

import os
import json

from cachewise.adapters import make_client


def main():
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY no encontrada")
    client = make_client("deepseek-direct")

    # Historial que crece como lo haria un bot en produccion.
    history = []
    print("=== TEST MULTI-TURNO cachewise + DeepSeek V4 (tus $2) ===\n")

    total_cost = 0.0
    for turn in range(5):
        history.append(
            {"role": "user", "content": f"Turno {turn}: dime quién eres en una frase."}
        )
        resp = client.chat(history, fidelity=1.0, enable_prethinker=True)
        usage = resp.get("usage", {})
        content = resp.get("message", {}).get("content", "")
        hit = usage.get("cache_hit_rate", 0.0)
        hit_tok = usage.get("prompt_cache_hit_tokens", 0)
        miss_tok = usage.get("prompt_cache_miss_tokens", 0)
        cost = usage.get("estimated_cost_usd", 0.0)
        total_cost += cost
        # Respuesta del modelo para este turno, la acumulamos al historial.
        history.append({"role": "assistant", "content": content})

        print(
            f"turn {turn}: cache_hit_rate={hit*100:.1f}% | "
            f"hit_tok={hit_tok} miss_tok={miss_tok} | "
            f"cost=${cost:.7f} | resp='{content[:40]}...'"
        )

    print(f"\nCosto total 5 turnos: ${total_cost:.7f}")
    print("Nota: cache_hit_rate viene del proveedor (DeepSeek), no es estimacion.")


if __name__ == "__main__":
    main()
