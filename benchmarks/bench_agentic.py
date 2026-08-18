"""Test agentico simulado: inyecta tool results volatiles cada turno.

Mide el cache_hit_rate REAL que devuelve DeepSeek cuando el historial
crece con resultados de herramientas (volatiles, distintos cada turno) —
el caso de uso de un agente. Compara sin comprimir (fidelity=1.0) vs
selector activo (fidelity=0.5, resume tool payloads).

El prefijo estable (~1152 tok) debe seguir cacheado; lo que cambia es el
porcentaje porque los tool results son miss.
"""

import os
import time

from cachewise.adapters import make_client


def fake_tool_result(turn: int) -> str:
    # Payload volatil: distinto cada turno (como lo seria en produccion).
    return (
        f"TOOL RESULT turn={turn} id=req_{turn:04d} "
        f"data=" + "x" * 400 + f" status=ok latency={3.2 + turn*0.1:.1f}ms "
        f"trace={os.urandom(8).hex()} payload=" + "y" * 400
    )


def run(fidelity: float, label: str):
    client = make_client("deepseek-direct")
    history = []
    print(f"\n=== {label} (fidelity={fidelity}) ===")
    for turn in range(5):
        # El agente "llama" una tool: assistant con tool_calls + tool result.
        call_id = f"call_{turn:04d}"
        history.append(
            {"role": "user", "content": f"Turno {turn}: consulta el estado del sistema."}
        )
        history.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {"name": "get_status", "arguments": "{}"},
                    }
                ],
            }
        )
        history.append(
            {"role": "tool", "tool_call_id": call_id, "content": fake_tool_result(turn)}
        )
        t0 = time.perf_counter()
        resp = client.chat(history, fidelity=fidelity, enable_prethinker=True)
        elapsed = time.perf_counter() - t0
        usage = resp.get("usage", {})
        hit = usage.get("cache_hit_rate", 0.0)
        hit_tok = usage.get("prompt_cache_hit_tokens", 0)
        miss_tok = usage.get("prompt_cache_miss_tokens", 0)
        cost = usage.get("estimated_cost_usd", 0.0)
        content = resp.get("message", {}).get("content", "")
        # El agente acumula su respuesta final al historial.
        history.append({"role": "assistant", "content": content})
        print(
            f"turn {turn}: hit_rate={hit*100:.1f}% | "
            f"hit_tok={hit_tok} miss_tok={miss_tok} | "
            f"tps~{usage.get('completion_tokens',0)/max(elapsed,1e-6):.1f} | "
            f"cost=${cost:.7f}"
        )


def main():
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY no encontrada")
    run(1.0, "SIN comprimir (tool payloads completos)")
    run(0.5, "CON selector (fidelity=0.5, resume tool payloads)")


if __name__ == "__main__":
    main()
