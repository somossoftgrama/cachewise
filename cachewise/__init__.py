"""LLM Delivery Optimizer para DeepSeek.

Modulo portable que mejora la entrega de DeepSeek V4 (via Nous Portal o API
directa + harness) en tres ejes:
  1. cache estable (ganancia pura, sin perder fidelidad)
  2. prethinker (razonamiento lacónico + salida al punto)
  3. selector de contenido (dial de fidelidad)

Interfaz OpenAI-compatible para usarlo en Hermes, OpenCode, LangChain, etc.
"""

__version__ = "0.1.0"
