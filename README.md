# LLM Delivery Optimizer (DeepSeek) v1

Optimizador de entrega para **DeepSeek V4** que mejora facturacion y claridad de respuesta sin que tengas que configurar nada. Instalas, apuntas tu `chat()` al optimizador, y "solo funciona".

## Tres palancas

| Palanca | Que hace | Trade-off |
|---|---|---
| **Cache estable** (siempre ON) | prefijo largo (>1024 tok, 256-alineado), nunca mutado | Ninguno (ganancia pura) |
| **Prethinker** (default ON) | directiva de estilo: razonamiento laconico + respuesta al punto | Minimo; mejora claridad |
| **Selector de contenido** (dial) | quita ruido redundante hasta el piso minimo necesario | Ninguno si respetas el piso |

## Instalacion

```bash
pip install -e .
```

## Uso rapido (3 lineas)

```python
from cachewise.adapters import make_client

client = make_client("nous-dsflash")  # o "deepseek-direct"
resp = client.chat([{"role": "user", "content": "¿Quien eres?"}])
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
conversacion** (historial acumulado) y muestra el `cache_hit_rate` que
devuelve DeepSeek. Requiere `DEEPSEEK_API_KEY` y env `deepseek-direct`.

```bash
export DEEPSEEK_API_KEY=tu_key
python benchmarks/bench_multiturn.py
```

Salida tipica (DeepSeek V4 Flash directo):

| Turno | cache_hit_rate | hit_tok | costo |
|---|---|---|---|
| 0 | 98.5% | 1152 | $0.0000136 |
| 1 | 94.7% | 1152 | $0.0000200 |
| 4 | 94.5% | 1280 | $0.0000219 |

El prefijo estable (~1152 tok) se cachea y se reusa turno a turno; solo se
paga el token nuevo de cada mensaje. Costo total 5 turnos: ~$0.0001.

## Tests

```bash
python -m pytest -q
```

| Archivo | Cubre |
|---|---|
| `tests/test_token_counter.py` | estimador heuristico de tokens (chars/4) |
| `tests/test_cache_aware.py` | prefijo estable: umbral, alineacion, no volatil |
| `tests/test_prethinker.py` | directiva laconica: inyeccion en system, conserva user |
| `tests/test_compress.py` | selector de contenido: reduce tokens, preserva instruccion |
| `tests/test_adapters.py` | make_client: env nous/deepseek, rechaza desconocido, prefijo estable |
| `tests/test_metrics.py` | measure (t/s, costo) y clarity_score |

Resultado: **22 tests verdes**.

## Entornos soportados

| env | endpoint | notas |
|---|---|---|
| `nous-dsflash` | Nous Portal `deepseek-v4-flash` | $0.11/$0.22 por 1M |
| `deepseek-direct` | API directa DeepSeek + harness | requiere `DEEPSEEK_API_KEY` |

## Para los demas (Hermes / OpenCode / LangChain)

`cachewise` es una libreria OpenAI-compatible. Solo cambias el cliente por
`make_client(...)` y conservas cache estable + prethinker + selector.

## Estado / alcance

- ✅ Cache estable, prethinker, selector de contenido
- ✅ CLI + benchmark + test multi-turno
- ✅ 22 tests verdes
- ⚠️ `nous-dsflash` listo; enrutamiento de `deepseek-v4-flash` en Nous Portal 404 en la cuenta de prueba (usar `deepseek-direct` con tus $2)
- Fuera de alcance v1: adapter de Command Code (plan Go bloquea Provider API), multi-provider mas alla de DeepSeek/Nous
