"""prethinker: directiva de estilo para razonamiento lacónico y salida al punto."""


PRETHINKER_DIRECTIVE = (
    "En tu razonamiento interno sé lacónico: una frase por decisión, "
    "sin narrar tus dudas en voz alta. En la respuesta ve directo al "
    "punto sin relleno ni explicaciones que el usuario no pidió."
)


def prethinker_directive() -> str:
    return PRETHINKER_DIRECTIVE


def apply_prethinker(messages: list[dict], directive: str = None) -> list[dict]:
    """Inyecta la directiva en el mensaje system sin tocar al usuario."""
    if directive is None:
        directive = PRETHINKER_DIRECTIVE
    out = [dict(m) for m in messages]
    has_system = any(m.get("role") == "system" for m in out)
    if has_system:
        for m in out:
            if m.get("role") == "system":
                if PRETHINKER_DIRECTIVE not in m.get("content", ""):
                    m["content"] = m["content"].rstrip() + "\n\n" + directive
                break
    else:
        out.insert(0, {"role": "system", "content": directive})
    return out
