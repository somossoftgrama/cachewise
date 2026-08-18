"""adapter multi-entorno: misma interfaz chat() para DeepSeek.

Entornos:
  - nous-dsflash: OpenAI-compat Nous Portal, model deepseek-v4-flash.
  - deepseek-direct: DeepSeekHarness (disable_thinking_by_default), deepseek-v4-flash.

Aplica las tres palancas: cache_aware (prefijo estable), prethinker
(directiva lacónica), compress (selector de contenido segun fidelity).
"""

import os

from .cache_aware import build_stable_prefix, CACHE_MIN_TOKENS
from .prethinker import apply_prethinker
from .compress import compress_history

BASE_POLICY = (
    "Eres el asistente de Rafael para Softgrama y Talentgrama. "
    "Responde en español latino neutro. Nunca uses voseo ni modismos "
    "regionales. Usa 'tú'. Mantén un tono profesional y directo. "
    "Prioriza resultados sobre perfección. Cuando redactes para clientes, "
    "usa lenguaje no técnico basado en beneficios. No menciones herramientas "
    "internas. Cumple con SOP: 50 por ciento anticipo al firmar."
)

NOUS_BASE = "https://inference-api.nousresearch.com/v1"


def _make_stable_system() -> str:
    return build_stable_prefix(BASE_POLICY, CACHE_MIN_TOKENS)


class OptimizedClient:
    def __init__(self, env: str):
        self.env = env
        self._system_prefix = _make_stable_system()
        if env == "nous-dsflash":
            self.model = "deepseek-v4-flash"; self._use_harness = False
        elif env == "deepseek-direct":
            self.model = "deepseek-v4-flash"; self._use_harness = True
        else:
            raise ValueError(f"Entorno desconocido: {env}")

    def _prepare(self, messages, fidelity, enable_prethinker):
        out = list(messages)
        has_system = any(m.get("role") == "system" for m in out)
        if has_system:
            for m in out:
                if m.get("role") == "system":
                    m["content"] = self._system_prefix + "\n\n" + m["content"]; break
        else:
            out.insert(0, {"role": "system", "content": self._system_prefix})
        if enable_prethinker:
            out = apply_prethinker(out)
        if fidelity < 1.0:
            out = compress_history(out, fidelity=fidelity)
        return out

    def chat(self, messages, fidelity=1.0, enable_prethinker=True, **kwargs):
        prepared = self._prepare(messages, fidelity, enable_prethinker)
        if self._use_harness:
            from deepseek_harness import DeepSeekHarness
            client = DeepSeekHarness(disable_thinking_by_default=True)
            return client.chat(model=self.model, messages=prepared, max_tokens=4096, **kwargs)
        from openai import OpenAI
        key = os.environ.get("NOUS_API_KEY") or self._nous_token()
        client = OpenAI(api_key=key, base_url=NOUS_BASE)
        resp = client.chat.completions.create(model=self.model, messages=prepared, max_tokens=4096, **kwargs)
        return {"message": {"role": "assistant", "content": resp.choices[0].message.content},
                "usage": {"prompt_tokens": resp.usage.prompt_tokens, "completion_tokens": resp.usage.completion_tokens}}

    def _nous_token(self) -> str:
        try:
            import json
            p = os.path.expandvars(r"%LOCALAPPDATA%/hermes/auth.json")
            with open(p) as f:
                auth = json.load(f)
            return auth["providers"]["nous"]["access_token"]
        except Exception:
            return os.environ.get("NOUS_API_KEY", "")


def make_client(env: str) -> OptimizedClient:
    return OptimizedClient(env)
