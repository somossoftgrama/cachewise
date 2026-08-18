"""selector de contenido (dial de fidelidad).

Quita contexto redundante segun el dial `fidelity` (0-1) sin bajar del piso
minimo donde la instruccion se degradaria. fidelity=1.0 mantiene todo;
valores menores quitan ruido (tool payloads ya consumidos, resumenes de
turnos viejos) pero SIEMPRE preservan system + instruccion activa del usuario.
"""

from .core import estimate_tokens

KEEP_LAST_DEFAULT = 2


def _is_active_instruction(m: dict) -> bool:
    return m.get("role") == "user" and m.get("content", "").strip() != ""


def compress_history(
    hist: list[dict],
    fidelity: float = 1.0,
    keep_last: int = KEEP_LAST_DEFAULT,
    drop_tool_payloads: bool = True,
    allow_degrade: bool = False,
) -> list[dict]:
    """Reduce tokens redundantes respetando el piso minimo de fidelidad.

    fidelity >= 1.0: devuelve historial igual.
    fidelity < 1.0: aplica reduccion proporcional al "ruido" (tool results
    viejos, turnos lejanos), manteniendo system + ultimos `keep_last` turnos
    + instruccion activa. Nunca borra la instruccion activa salvo que
    allow_degrade=True (no por defecto).
    """
    if fidelity >= 1.0:
        return [dict(m) for m in hist]

    system = [m for m in hist if m.get("role") == "system"]
    non_system = [m for m in hist if m.get("role") != "system"]

    # La instruccion activa (ultimo user) SIEMPRE se preserva integra.
    last_user_idx = max(
        (i for i, m in enumerate(non_system) if m.get("role") == "user"),
        default=-1,
    )
    active = non_system[last_user_idx] if last_user_idx >= 0 else None
    earlier = [m for i, m in enumerate(non_system) if i != last_user_idx]

    reduced = []
    for m in earlier:
        role = m.get("role")
        content = m.get("content", "")
        # Quitar payloads de tool ya consumidos (ruido tipico).
        if role == "tool" and drop_tool_payloads:
            if estimate_tokens(content) > 200:
                # Conservar solo un resumen corto, no el payload entero.
                # IMPORTANTE: preservar tool_call_id y demas campos del mensaje
                # original, si no DeepSeek/OpenAI rechazan el request.
                snippet = content[:120].replace("\n", " ")
                summarized = dict(m)
                summarized["content"] = f"[resumen] {snippet}…"
                reduced.append(summarized)
                continue
        # Turnos lejanos: acortar si son muy largos.
        if estimate_tokens(content) > 600:
            snippet = content[:300].replace("\n", " ")
            shortened = dict(m)
            shortened["content"] = f"{snippet}…"
            reduced.append(shortened)
        else:
            reduced.append(dict(m))

    out = list(system) + reduced
    if active is not None:
        out.append(active)

    # Salvaguarda: la instruccion activa (ultimo user) SIEMPRE debe existir.
    if not any(_is_active_instruction(m) for m in out):
        if not allow_degrade:
            # Restaurar el historial original para no degradar.
            return [dict(m) for m in hist]
    return out
