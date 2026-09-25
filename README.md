# Agente de informe semanal: mercado y sector agro

> **Estado:** en construcción. Hito 3 de 7: corrida 1 hecha con el contrato v1; falta decidir la iteración 1. Las secciones marcadas como _pendiente_ se completan en el hito que corresponde, justo después de cada corrida y no al final, para que el registro no dependa de la memoria.

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
4. **Invocación:** `python scripts/correr_agente.py --lunes 2026-09-07 --version v1 --archivo corrida_1_semana_2026-09-07.md`. El script usa el CLI de Claude Code en modo no interactivo (requiere `claude auth login`) y:
   - pasa el contenido de `system_prompt.md` como `--system-prompt`, es decir, como system prompt real y no pegado en el mensaje;
   - pasa `user_prompt.md`, con la semana, la versión y el archivo de destino completados, como mensaje del usuario;
   - usa el modelo `sonnet` (en la corrida 1 se resolvió como `claude-sonnet-5`) y le da solo cuatro herramientas: Read, Glob, Grep y Write, sin shell ni web;
   - deja que el agente escriba el informe en `salidas/` y guarda `salidas/<archivo>.meta.json` con el hash del contrato usado, el modelo, los turnos, los tokens y los archivos que el agente abrió de verdad.

   Está hecho en Python y no en PowerShell porque PowerShell 5.1 rompe las comillas dobles de un texto largo al pasarlo como argumento. Antes de la primera corrida se comprobó que el system prompt llega íntegro: el agente respondió bien siete preguntas puntuales sobre su contenido, incluida la última sección.
5. **Chequeo de formato:** `python scripts/validar_salida.py salidas/<archivo>.md`.

## 4. Corridas

| Corrida | Semana | Contrato | Salida | Validador |
|---|---|---|---|---|
| 1 | 2026-09-07 al 2026-09-11 | v1 | [`corrida_1_semana_2026-09-07.md`](salidas/corrida_1_semana_2026-09-07.md) | 21/21 |
| 2 | 2026-09-14 al 2026-09-18 | v2 | _pendiente_ | _pendiente_ |
| 3 | 2026-09-21 al 2026-09-25 | v3 | _pendiente_ | _pendiente_ |

Además, después de cada cambio de contrato se vuelve a correr la semana anterior con la versión nueva. Esa corrida extra no cuenta entre las tres y sirve para atribuir el cambio en la salida al cambio en el prompt y no a que cambiaron los datos.

### Corrida 1: contrato v1 sobre la semana 2026-09-07

**Cómo fue:** 29 turnos, 571 segundos, modelo `claude-sonnet-5`, 28 llamadas a herramientas (12 Read, 12 Grep, 3 Glob, 1 Write). Los datos completos están en [`salidas/corrida_1_semana_2026-09-07.md.meta.json`](salidas/corrida_1_semana_2026-09-07.md.meta.json). El agente respondió `salidas/corrida_1_semana_2026-09-07.md, 10/10`.

**Qué salió bien (verificado contra los textos de origen, no supuesto):**
- Estructura: el validador da 21/21. El máximo fue 32 palabras en un bullet, 17 en una celda y 1.010 palabras en total, contra límites de 35, 25 y 1.200.
- Cifras: contrasté 24 líneas de tablas de cierre (tipo de cambio, brecha, Cresud, Merval, LECAP, Profertil, Bioceres) y unas 25 afirmaciones de los dailys. Todo coincide con el texto de origen, salvo lo señalado en F4 y F5.
- Contradicciones entre fuentes: el agente detectó y declaró en la sección 5 que el daily y el cierre difieren sobre Cresud (jueves: +6,3% en el cierre contra -1,2% en el daily; martes: +2,0% contra +3,0%). Comprobé que ambas cifras están en las fuentes.
- El bloque sectorial (4.2) trae datos reales: soja comercializada 53,6% contra 60,1% de promedio, tasas de las ON de Profertil y la caída de Bioceres.

**Qué falló (con evidencia textual):**

- **F1. Las columnas "Cierre lunes" y "Cierre viernes" de la tabla 4.1 no significan lo mismo en todas las filas.** Para las variables que solo existen en los dailys, el agente las llenó con cotizaciones intradía o con datos de otro día:
  - `| Petróleo (Brent) | 97,3 (intradía) | 104,7 (intradía) | +7,6% |`
  - `| Treasury 10 años | n/d | 4,92% (intradía) |`
  - `| Riesgo país | 490 pbs (cierre del 4/9; Globales sin operar el 7/9) | n/d (bajo 500 pbs el 9/9) |`

  El propio agente tuvo que explicarlo en la sección 5: "Brent (lun y vie) y Treasury (vie) son cotizaciones intradía de los dailys". Además el +7,6% del Brent sale de dos cotizaciones tomadas a horas distintas, y el resumen dice que el Brent llegó a US$101,6 el 9/9 mientras la tabla dice 104,7. Con este formato, cada semana podría llenar esas celdas con criterios distintos, y eso rompe la comparabilidad.
- **F2. Leyó archivos fuera de la semana.** Ejecutó `Glob **/README*` y `Read README.md`, aunque la restricción dice "Usá solo la información de los archivos de la semana". Esta corrida no aisló el entorno: el agente corría dentro del repo y podía ver todo.
- **F3. "Insumos leídos: 10/10" es una afirmación demasiado generosa.** `mie_cierre.txt` nunca se abrió con Read: solo apareció en búsquedas con Grep y la salida no lo cita ni una vez (0 etiquetas `[mie-cierre]`). `jue_cierre` y `vie_cierre` se leyeron por tramos. Aun así, la fila del miércoles dice `| Miércoles | Sí | Sí | |`, sin observaciones.
- **F4. Una fecha que no está en los informes.** La expectativa 5 dice "Reunión del 16/9". Ningún daily de la semana menciona esa fecha: el del lunes dice "la semana que viene" y el del viernes "la reunión de septiembre". Es conocimiento externo, que la restricción prohíbe.
- **F5. Una etiqueta de fuente de más.** La expectativa 2 cita `[jue-daily] [lun-daily]`, pero el texto sobre "FX estable" y commodities está solo en el del jueves.

**Lectura:** el validador aprobó 21 de 21 y aun así hay cinco fallas de fondo. Un chequeo de estructura no reemplaza leer el contenido contra las fuentes. Ninguna de las cinco es un error de cifras: son fallas de contrato (formato ambiguo, restricciones que no se cumplen) y de entorno.

**Decisión pendiente:** qué pieza del contrato tocar en la iteración 1.

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
