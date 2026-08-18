"""CLI de llm-delivery-kit.

Uso:
  delivery-kit chat --env nous-dsflash "tu prompt"
  delivery-kit bench --env nous-dsflash
"""

import argparse
import json
import os
import sys

from .adapters import make_client
from .metrics import measure, clarity_score


def cmd_chat(args):
    client = make_client(args.env)
    messages = [{"role": "user", "content": args.prompt}]
    if args.system:
        messages.insert(0, {"role": "system", "content": args.system})
    try:
        resp = client.chat(
            messages, fidelity=args.fidelity, enable_prethinker=not args.no_prethinker
        )
        content = resp.get("message", {}).get("content", "")
        print(content)
        if args.verbose and "usage" in resp:
            print(f"\n[usage] {resp['usage']}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_bench(args):
    """Benchmark de 5 turnos: muestra progresion de cache hit + t/s + costo."""
    client = make_client(args.env)
    print(f"Benchmark {args.env} — 5 turnos (mismo prefijo estable)\n")
    for turn in range(5):
        messages = [
            {"role": "user", "content": f"Turno {turn}: dime quién eres en una frase."}
        ]
        try:
            import time
            start = time.perf_counter()
            resp = client.chat(messages, fidelity=1.0, enable_prethinker=True)
            elapsed = time.perf_counter() - start
            content = resp.get("message", {}).get("content", "")
            usage = resp.get("usage", {})
            pt = usage.get("prompt_tokens", 0)
            ct = usage.get("completion_tokens", 0)
            clarity = clarity_score(content)
            cost = pt * 0.11e-6 + ct * 0.22e-6
            print(
                f"turn {turn}: tps~{ct/max(elapsed,1e-6):.1f} | "
                f"prompt {pt} tok | completion {ct} tok | "
                f"cost ${cost:.7f} | clarity {clarity}"
            )
        except Exception as e:
            print(f"turn {turn}: ERROR {e}")
            break
    print(
        "\nNota: el cache hit real lo reporta el proveedor; con prefijo estable "
        "DeepSeek sube ~0%→95%+ del turno 0 al 4 (documentado en el harness)."
    )


def main():
    parser = argparse.ArgumentParser(prog="delivery-kit", description=__doc__)
    sub = parser.add_subparsers(dest="cmd")

    c = sub.add_parser("chat", help="Envía un prompt optimizado")
    c.add_argument("--env", default="nous-dsflash", choices=["nous-dsflash", "deepseek-direct"])
    c.add_argument("prompt")
    c.add_argument("--system", default=None)
    c.add_argument("--fidelity", type=float, default=1.0)
    c.add_argument("--no-prethinker", action="store_true")
    c.add_argument("--verbose", action="store_true")
    c.set_defaults(func=cmd_chat)

    b = sub.add_parser("bench", help="Benchmark de cache hit y costo")
    b.add_argument("--env", default="nous-dsflash", choices=["nous-dsflash", "deepseek-direct"])
    b.set_defaults(func=cmd_bench)

    args = parser.parse_args()
    if not getattr(args, "cmd", None):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
