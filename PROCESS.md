# Proceso de diseno — LLM Delivery Optimizer (DeepSeek)

Documento de trazabilidad: como se llego de la idea al modulo, las decisiones y las pruebas reales.

## 1. Origen

Rafael vio un post sobre `deepseek-harness` (HenryZ838978) que corrige el contrato de protocolo de V4. El harness documenta un *prefix cache* con umbral de **1024 tokens** y bloque de **256 tokens**: si no mutas el prefijo, el hit-rate sube de **0% a ~95%** y el input pasa de **$0.14/M a $0.0028/M** (≈50× mas barato).

## 2. La tension del diseno

Rafael pidio dos cosas que parecian opuestas: mantener t/s sin bajar tokens, y simplificar para ahorrar. Resolucion: **cache estable** (ganancia pura, reusa prefijo) y **compresion** (opt-in, quita redundancia) son estrategias separadas y conmutables. Luego afino a un **selector de contenido** con dial continuo de fidelidad.

## 3. Tres palancas

| Palanca | Mecanismo |
|---|---|
| Cache estable | prefijo >1024 tok, 256-alineado, nunca mutado |
| Prethinker | directiva de estilo: razonamiento lacónico + salida al punto |
| Selector (dial) | quita ruido hasta el piso minimo, preserva instruccion activa |

## 4. Pruebas reales

**Benchmark DeepSeek V4 Flash DIRECTO (API + harness):**
```
turn 0: tps~0.7  | prompt 1170 tok | cost $0.0001338 | clarity 1.0
turn 1: tps~16.5 | prompt 1170 tok | cost $0.0001351 | clarity 1.0
turn 4: tps~17.0 | prompt 1170 tok | cost $0.0001346 | clarity 1.0
```
El salto 0.7 → 16.5 t/s entre turno 0 y 1 es la prueba empirica del cache hit.

**Test multi-turno (cache hit real del proveedor):**
```
turn 0: cache_hit_rate=98.5% | hit_tok=1152
... 
turn 4: cache_hit_rate=94.5% | hit_tok=1280
```

## 5. Uso agentico

En agentes se inyectan tool results volatiles. El prefijo estable se sigue cacheando (hit_tok crece 1152→2176), pero el % baja a ~83-90% porque esos resultados son miss por naturaleza. Para agentes, conviene `fidelity=1.0` (sin comprimir) para maximizar el cache hit.

## 6. Pendientes

- `deepseek-v4-flash` en Nous Portal inferencia dio 404 en la cuenta; env `nous-dsflash` listo, falta enrutamiento.
- Adapter de Command Code fuera de alcance v1 (plan Go bloquea API).
- Bug corregido: el selector perdia `tool_call_id` al resumir tool messages (ahora lo preserva).
