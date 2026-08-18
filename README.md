# LLM Delivery Optimizer (DeepSeek) v1

Optimizador de entrega para **DeepSeek V4** que mejora facturación y claridad
de respuesta sin que tengas que configurar nada. Instalas, apuntas tu
`chat()` al optimizador, y "solo funciona".

## Por qué existe

DeepSeek V4 tiene un *prefix cache*: si reusas el mismo prefijo estable entre
turnos, el input repetido se vuelve hasta **50× más barato** (documentado en
el harness de DeepSeek: hit-rate sube ~0% → 95%+ del turno 0 al 4). Además,
un *razonamiento lacónico* + *salida al punto* mejoran la claridad percibida
por el usuario final sin gastar más.

Este módulo se monta **encima del harness** (corrección de protocolo) y añade
la economía de la entrega.

## Tres palancas

| Palanca | Qué hace | Trade-off |
|---|---|---
| **Cache estable** (siempre ON) | prefijo largo (>1024 tok, 256-alineado), nunca mutado | Ninguno (ganancia pura) |
| **Prethinker** (default ON) | directiva de estilo: razonamiento lacónico + respuesta al punto | Mínimo; mejora claridad |
| **Selector de contenido** (dial) | quita ruido redundante hasta el piso mínimo necesario | Ninguno si respetas el piso; degrada solo con `allow_degrade=True` |

El **dial de fidelidad** (`fidelity` 0.0–1.0):
- `1.0` = envía todo (máxima claridad, mayor costo).
- `<1.0` = quita redundancia (tool payloads viejos, turnos lejanos) pero
  **siempre preserva la instrucción activa del usuario**.

## Instalación

```bash
pip install -e .
```

## Uso rápido (3 líneas)

```python
from cachewise.adapters import make_client

client = make_client("nous-dsflash")  # o "deepseek-direct"
resp = client.chat([{"role": "user", "content": "¿Quién eres?"}])
print(resp["message"]["content"])
```

## CLI

```bash
# Chat optimizado
cachewise chat --env nous-dsflash "tu prompt"

# Benchmark de 5 turnos (cache hit + t/s + costo + claridad)
cachewise bench --env deepseek-direct
```

## Test multi-turno (cache hit real del proveedor)

`benchmarks/bench_multiturn.py` hace 5 llamadas `chat()` a la **misma
conversación** (historial acumulado, como un bot en producción) y muestra
el `cache_hit_rate` y costo por turno que devuelve DeepSeek. Requiere
`DEEPSEEK_API_KEY` y el env `deepseek-direct`.

```bash
export DEEPSEEK_API_KEY=tu_key
python benchmarks/bench_multiturn.py
# o vía el script registrado:
cachewise-bench
```

Salida típica (tus $2, DeepSeek V4 Flash directo):

| Turno | cache_hit_rate | hit_tok | costo |
|---|---|---|---
| 0 | 98.5% | 1152 | $0.0000136 |
| 1 | 94.7% | 1152 | $0.0000200 |
| 4 | 94.5% | 1280 | $0.0000219 |

El prefijo estable (~1152 tok) se cachea y se reusa turno a turno; solo
se paga el token nuevo de cada mensaje. Costo total 5 turnos: ~$0.0001.

## Entornos soportados

| env | endpoint | notas |
|---|---|---
| `nous-dsflash` | Nous Portal `deepseek-v4-flash` | $0.11/$0.22 por 1M |
| `deepseek-direct` | API directa DeepSeek + harness | requiere `DEEPSEEK_API_KEY` |

## Para los demás (Hermes / OpenCode / LangChain)

Interfaz OpenAI-compatible: cualquier framework de agentes puede usar
`OptimizedClient.chat(messages)` como su capa de `chat()`. No acoplado a
Hermes.

## Estado v1

- ✅ Cache estable + validación offline (`dsh estimate`)
- ✅ Prethinker (directiva lacónica)
- ✅ Selector de contenido (dial de fidelidad)
- ✅ Adapter multi-entorno
- ✅ Métricas (t/s, costo, clarity_score)
- ✅ CLI + benchmark

**Fuera de alcance v1:** adapter de Command Code (plan Go bloquea Provider
API), multi-provider más allá de DeepSeek/Nous, publicación en GitHub
público.
