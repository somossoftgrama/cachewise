"""selector de contenido (dial de fidelidad)."""

from .core import estimate_tokens

KEEP_LAST_DEFAULT = 2


def _is_active_instruction(m: dict) -> bool:
    return m.get("role") == "user" and m.get("content", "").strip() != ""


def compress_history(hist: list[dict], fidelity: float = 1.0,
                    keep_last: int = KEEP_LAST_DEFAULT,
                    drop_tool_payloads: bool = True,
                    allow_degrade: bool = False) -> list[dict]:
    """Reduce tokens redundantes respetando el piso minimo de fidelidad."""
    if fidelity >= 1.0:
        return [dict(m) for m in hist]
    system = [m for m in hist if m.get("role") == "system"]
    non_system = [m for m in hist if m.get("role") != "system"]
    last_user_idx = max((i for i, m in enumerate(non_system) if m.get("role") == "user"), default=-1)
    active = non_system[last_user_idx] if last_user_idx >= 0 else None
    earlier = [m for i, m in enumerate(non_system) if i != last_user_idx]
    reduced = []
    for m in earlier:
        role = m.get("role")
        content = m.get("content", "")
        if role == "tool" and drop_tool_payloads and estimate_tokens(content) > 200:
            snippet = content[:120].replace("\n", " ")
            reduced.append({"role": role, "content": f"[resumen] {snippet}…"})
            continue
        if estimate_tokens(content) > 600:
            snippet = content[:300].replace("\n", " ")
            reduced.append({"role": role, "content": f"{snippet}…"})
        else:
            reduced.append(dict(m))
    out = list(system) + reduced
    if active is not None:
        out.append(active)
    if not any(_is_active_instruction(m) for m in out):
        if not allow_degrade:
            return [dict(m) for m in hist]
    return out
