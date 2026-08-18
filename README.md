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

## Uso rapido

```python
from cachewise.adapters import make_client
client = make_client("nous-dsflash")
resp = client.chat([{"role": "user", "content": "Quien eres?"}])
print(resp["message"]["content"])
```

## CLI

```bash
cachewise chat --env nous-dsflash "tu prompt"
cachewise bench --env hy3
```

## Entornos

| env | endpoint | notas |
|---|---|---
| `nous-dsflash` | Nous Portal `deepseek-v4-flash` | $0.11/$0.22 por 1M |
| `deepseek-direct` | API directa DeepSeek + harness | requiere `DEEPSEEK_API_KEY` |
| `hy3` | Nous Portal `tencent/hy3:free` | gratis, demo |
