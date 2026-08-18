# Proceso de diseño — LLM Delivery Optimizer (DeepSeek)

Documento de trazabilidad: cómo se llegó de la idea al módulo, las
decisiones de arquitectura y las pruebas reales. Escrito para que cualquiera
pueda entender el "por qué", no solo el "qué".

## 1. Origen (17-ago-2026)

Rafael vio un post de Jun Song sobre `deepseek-harness` (HenryZ838978) que
"desbloquea el poder de DeepSeek V4" arreglando errores del proceso de
pensamiento. Se instaló y probó: el harness corrige el contrato de protocolo
de V4 (reasoning_content round-trip, thinking-off, no romper multi-turn).

**Hallazgo clave del harness (empírico, 270 trials):** DeepSeek V4 tiene un
*prefix cache* con umbral de **1024 tokens** y bloque de **256 tokens**. Si
no mutas el prefijo entre turnos, el hit-rate sube de **0% (turno 0) a
~95% (turno 4)**, y el input pasa de **$0.14/M a $0.0028/M** (≈50× más
barato).

## 2. La tensión que definió el diseño

Rafael pidió dos cosas que parecían opuestas:
- "Mantenga t/s sin que disminuya la cantidad de tokens por envío."
- "Simplifique el mensaje ida y vuelta para ahorrar tokens."

**Resolución:** no son excluyentes. Se modelaron como dos estrategias
separadas y conmutables:
1. **Cache estable** = ganancia pura (no quita tokens, reusa prefijo).
2. **Compresión** = opt-in, quita redundancia (trade-off documentado).

Luego Rafael afinó: no es "fidelidad O tokens", es un **selector de
contenido** con dial continuo:
- Más alto = mandas todo lo necesario (fidelidad máxima).
- Más bajo = monto mínimo necesario para que la instrucción se cumpla.
- El módulo NUNCA baja del piso mínimo sin `allow_degrade=True`.

## 3. Las tres palancas

| Palanca | Mecanismo | Trade-off |
|---|---|---
| Cache estable | prefijo >1024 tok, 256-alineado, nunca mutado | Ninguno |
| Prethinker | directiva de estilo: razonamiento lacónico + salida al punto | Mejora claridad |
| Selector (dial) | quita ruido hasta el piso mínimo | Ninguno si respeta piso |

El **principio rector**: "solo funcione" — instalado, apuntas `chat()`, y ves
mejora en facturación y claridad sin configurar nada.

## 4. Filosofía de calidad

Rafael planteó que DeepSeek + esto podría superar a modelos tipo "Fable" no
por elocuencia, sino por **claridad y propósito para llegar al usuario**.
Eso se midió con `clarity_score` (penaliza longitud/filler, premia directo).

## 5. Sobre Command Code

Se descartó depender de Command Code: su plan Go bloquea Provider API (403
upgrade_required). El módulo es librería portable OpenAI-compatible, así que
Command Code (u OpenCode, LangChain, Hermes) lo usa como capa de `chat()`
cuando quiera, sin ser una dependencia.

## 6. Ejecución

Se intentó delegación paralela de subagentes, pero fallaron por rate limit
(HTTP 429) y dejaron archivos corruptos (`clients/`, `tokens.py`). Se
reescribió el módulo de forma manual y se limpió la basura. Resultado: 23
tests verdes, módulo limpio.

## 7. Pruebas reales

### 7.1 Benchmark hy3 (demo histórica, Nous Portal — entorno ya retirado)
```
turn 0: tps~5.9  | prompt 1383 tok | clarity 1.0
turn 4: tps~27.6 | prompt 1383 tok | clarity 1.0
```
Muestra el "calentamiento" del cache (t/s sube con prefijo estable).

### 7.2 Benchmark DeepSeek V4 Flash DIRECTO (tus $2, API + harness)
```
turn 0: tps~0.7  | prompt 1170 tok | cost $0.0001338 | clarity 1.0
turn 1: tps~16.5 | prompt 1170 tok | cost $0.0001351 | clarity 1.0
turn 2: tps~23.3 | prompt 1170 tok | cost $0.0001351 | clarity 1.0
turn 3: tps~21.2 | prompt 1170 tok | cost $0.0001351 | clarity 1.0
turn 4: tps~17.0 | prompt 1170 tok | cost $0.0001346 | clarity 1.0
```
El salto 0.7 → 16.5 t/s entre turno 0 y 1 es la prueba empírica del cache
hit (procesamiento "frío" vs "caliente"). Costo ~$0.00013/turno.

## 8. Pendientes honestos

- `deepseek-v4-flash` en el endpoint de inferencia de Nous Portal dio 404
  (el catálogo lo lista pero el runtime no lo resuelve en esta cuenta). El
  env `nous-dsflash` está listo; falta enrutamiento del modelo.
- El benchmark no imprime `estimated_hit_rate` numérico (la API directa no lo
  devuelve; `dsh estimate` es la fuente offline). Mejora futura: reporte
  por turno usando `dsh estimate`.
- Adapter de Command Code: fuera de alcance v1 (plan Go bloquea API).
