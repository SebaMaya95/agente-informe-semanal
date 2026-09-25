# Agente de informe semanal: mercado y sector agro

> **Estado:** en construcción. Hito 2 de 7: contrato v1 escrito y congelado, todavía sin correr. Las secciones marcadas como _pendiente_ se completan en el hito que corresponde, justo después de cada corrida y no al final, para que el registro no dependa de la memoria.

## 1. La tarea

Cada semana, un agente lee los 5 informes _daily_ y los 5 informes de _cierre de día_ (lunes a viernes) y escribe un informe semanal estructurado con: (a) resumen de la semana, (b) expectativas explícitas que aparecen en los informes y cómo terminaron, y (c) un apartado sobre lo que puede afectar al sector agro, desde la macro (dólar, brecha, tasas, riesgo país) hasta algún dato propio del sector cuando los informes lo traen.

La tarea es recurrente (semanal), tiene insumos reales y la salida tiene la misma forma todas las semanas, para poder comparar una corrida con la siguiente.

## 2. El contrato: las seis piezas

| Pieza | Dónde está | Archivo |
|---|---|---|
| 1. Rol | system | [`system_prompt.md`](system_prompt.md), sección 1 |
| 2. Contexto | system (lo estable: qué son los informes, cómo se leen) y user (lo variable: semana, carpeta, versión) | ambos, sección 2 |
| 3. Tarea | user (el pedido puntual), con una frase general en system | [`user_prompt.md`](user_prompt.md), sección 3 |
| 4. Restricciones | system | `system_prompt.md`, sección 4 |
| 5. Formato | system (estructura exacta del informe) | `system_prompt.md`, sección 5 |
| 6. Ejemplos | system (filas de ejemplo con datos inventados) | `system_prompt.md`, sección 6 |

Cada versión del contrato queda congelada en [`iteraciones/`](iteraciones/) (`v1/`, `v2/`, `v3/`). Los archivos de la raíz son siempre la versión vigente; al cierre, la final.

### Decisiones de diseño previas a v1

- **"Expectativas explícitas" en lugar de "esperado vs. ocurrido".** La idea inicial era comparar lo que el daily esperaba con lo que mostró el cierre. Al leer los informes resultó que el cierre son solo tablas de precios, sin texto, y que el daily cuenta lo que pasó el día anterior y adelanta algunas expectativas sueltas. Por eso el agente lista las expectativas explícitas de los dailys y marca su estado al viernes.
- **El agro casi no aparece en los dailys.** Un dato sectorial por semana como máximo, y a veces ninguno. El apartado agro se apoya en una tabla fija de diez variables macro, y el bloque sectorial admite una frase fija de "sin información".
- **Los informes originales no se publican.** Traen un aviso que prohíbe copiar o distribuir su contenido. Quedan fuera del repo (`.gitignore`), la fuente no se nombra en ningún archivo y las salidas son síntesis propia con cifras puntuales, sin reproducir tablas ni párrafos.
- **Los textos de los mails no se usan.** Los PDF son autocontenidos.
- **Semanas usadas.** Corrida 1: 7 al 11 de septiembre de 2026. Corrida 2: 14 al 18. Corrida 3: 21 al 25 (el viernes 25 todavía no había llegado cuando se armó el contrato, por eso la corrida 3 se hace después).
- **Lo que se sabía de los datos al escribir v1.** Durante la exploración de los insumos se detectaron irregularidades, por ejemplo que el cierre del lunes 14 llegó en inglés, con menos páginas y con la portada fechada el 15. v1 no incluye reglas para esos casos a propósito: se agregan solo si una corrida muestra que fallan.
- **Validador de formato.** [`scripts/validar_salida.py`](scripts/validar_salida.py) chequea estructura (títulos, columnas, filas, valores permitidos, fuentes, extensión, anonimato) y se escribió a partir de la especificación, antes de ver ninguna salida. No juzga la calidad del análisis. El chequeo de anonimato lee sus términos de un archivo local que no se publica (`insumos/terminos_prohibidos.txt`); sin ese archivo, el chequeo se omite y el validador lo avisa.

## 3. Cómo se corre

1. **Paso 0, manual y fuera del contrato:** los informes llegan por mail con el PDF adjunto; se descargan y se ubican en `insumos/semana_<fecha del lunes>/` con los nombres `lun|mar|mie|jue|vie` + `_daily.pdf` o `_cierre.pdf`. Esa carpeta no se publica.
2. **Texto plano:** `python scripts/extraer_texto.py` convierte cada PDF en `.txt` (requiere `pypdf`).
3. **Agente:** `python scripts/preparar_agente.py` arma el agente con el contenido exacto de `system_prompt.md`.
4. **Invocación:** _pendiente: se documenta cuando quede definido y probado cómo se invoca al agente con el user prompt._
5. **Chequeo de formato:** `python scripts/validar_salida.py salidas/<archivo>.md`.

## 4. Corridas

| Corrida | Semana | Contrato | Salida | Validador |
|---|---|---|---|---|
| 1 | 2026-09-07 al 2026-09-11 | v1 | _pendiente_ | _pendiente_ |
| 2 | 2026-09-14 al 2026-09-18 | v2 | _pendiente_ | _pendiente_ |
| 3 | 2026-09-21 al 2026-09-25 | v3 | _pendiente_ | _pendiente_ |

Además, después de cada cambio de contrato se vuelve a correr la semana anterior con la versión nueva. Esa corrida extra no cuenta entre las tres y sirve para atribuir el cambio en la salida al cambio en el prompt y no a que cambiaron los datos.

## 5. Iteración 1

- **Qué falló (textual):** _pendiente_
- **Pieza del contrato que toqué:** _pendiente_
- **Cambio (antes → después):** _pendiente_
- **Qué cambió en la salida:** _pendiente_
- **Commit:** _pendiente_

## 6. Iteración 2

- **Qué falló (textual):** _pendiente_
- **Pieza del contrato que toqué:** _pendiente_
- **Cambio (antes → después):** _pendiente_
- **Qué cambió en la salida:** _pendiente_
- **Commit:** _pendiente_

## 7. Comparación de las tres corridas

_Pendiente: qué se mantuvo fijo en la estructura de salida y qué varió._

## 8. Reflexión: qué aprendí del contrato

_Pendiente._

## 9. Nota sobre los datos

Los informes originales (mails y PDF) no se publican en este repositorio: `insumos/` y los archivos `.pdf`, `.eml` y `.msg` están excluidos por `.gitignore`. Solo se publican los prompts, las salidas, los scripts y este README.
