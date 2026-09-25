# Agente de informe semanal: mercado y sector agro

> **Estado:** entrega completa, hito 7 de 7: tres corridas y dos iteraciones documentadas. La corrida 3 se hizo con la semana incompleta (lunes a jueves, 8 de 10 archivos) porque los informes del viernes 25/9 todavía no existían; puede repetirse cuando estén. Las secciones marcadas como _pendiente_ se completan en el hito que corresponde, justo después de cada corrida y no al final, para que el registro no dependa de la memoria.

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
- **Semanas usadas.** Corrida 1: 7 al 11 de septiembre de 2026. Corrida 2: 14 al 18. Corrida 3: 21 al 25. El viernes 25 todavía no había llegado, así que la corrida 3 se hizo el jueves 24/9 a la noche con lunes a jueves (8 de 10 archivos), y queda documentada como semana incompleta.
- **Lo que se sabía de los datos al escribir v1.** Durante la exploración de los insumos se detectaron irregularidades, por ejemplo que el cierre del lunes 14 llegó en inglés, con menos páginas y con la portada fechada el 15. v1 no incluye reglas para esos casos a propósito: se agregan solo si una corrida muestra que fallan.
- **Validador de formato.** [`scripts/validar_salida.py`](scripts/validar_salida.py) chequea estructura (títulos, columnas, filas, valores permitidos, fuentes, extensión, anonimato) y se escribió a partir de la especificación, antes de ver ninguna salida. Tiene una especificación por versión del contrato (`--spec v1`, `v2` o `v3`); cada una se escribió antes de correr la versión correspondiente. No juzga la calidad del análisis. El chequeo de anonimato lee sus términos de un archivo local que no se publica (`insumos/terminos_prohibidos.txt`); sin ese archivo, el chequeo se omite y el validador lo avisa.

## 3. Cómo se corre

1. **Paso 0, manual y fuera del contrato:** los informes llegan por mail con el PDF adjunto; se descargan y se ubican en `insumos/semana_<fecha del lunes>/` con los nombres `lun|mar|mie|jue|vie` + `_daily.pdf` o `_cierre.pdf`. Esa carpeta no se publica.
2. **Texto plano:** `python scripts/extraer_texto.py` convierte cada PDF en `.txt` (requiere `pypdf`).
3. **Agente:** `python scripts/preparar_agente.py` arma el agente con el contenido exacto de `system_prompt.md`.
4. **Invocación:** `python scripts/correr_agente.py --lunes 2026-09-14 --version v2 --archivo corrida_2_semana_2026-09-14.md`. El script usa el CLI de Claude Code en modo no interactivo (requiere `claude auth login`) y:
   - pasa el contenido de `system_prompt.md` como `--system-prompt`, es decir, como system prompt real y no pegado en el mensaje;
   - pasa `user_prompt.md`, con la semana, la versión y el archivo de destino completados, como mensaje del usuario;
   - usa el modelo `sonnet` (en la corrida 1 se resolvió como `claude-sonnet-5`) y le da solo cuatro herramientas: Read, Glob, Grep y Write, sin shell ni web;
   - desde la corrida 2 lo corre **aislado**: en una carpeta temporal que contiene solo los `.txt` de la semana y una carpeta `salidas/` vacía, con las herramientas de archivos confinadas a esa carpeta (`--restricted`). Así el agente no puede leer el README, los scripts, otras semanas ni los contratos anteriores. La corrida 1 no estaba aislada y el agente leyó el README (falla F2). Es un cambio de entorno, no de contrato;
   - deja que el agente escriba el informe, lo copia sin tocarlo a `salidas/` y guarda `<archivo>.meta.json` con el hash del contrato usado, el modelo, los turnos, los tokens, los archivos que el agente abrió de verdad, cuánto leyó de cada uno (cobertura de lectura, desde el hito 6) y si abrió alguno fuera de la semana.

   Está hecho en Python y no en PowerShell porque PowerShell 5.1 rompe las comillas dobles de un texto largo al pasarlo como argumento. Antes de la primera corrida se comprobó que el system prompt llega íntegro: el agente respondió bien siete preguntas puntuales sobre su contenido, incluida la última sección.
5. **Chequeo de formato:** `python scripts/validar_salida.py --spec v3 salidas/<archivo>.md`.
6. **Revisión de contenido:** el validador no juzga si lo que dice el informe es cierto. Para eso se contrastan las afirmaciones contra los textos de origen y se usa como ayuda `python scripts/chequear_cifras.py salidas/<archivo>.md <fecha del lunes>`, que lista las cifras específicas (tres o más dígitos) que no aparecen en los insumos. Las cifras cortas (0,5; 3,5) aparecen por casualidad en cualquier texto, por eso no se chequean, y las calculadas por el agente hay que recalcularlas a mano.

## 4. Corridas

| Corrida | Semana | Contrato | Salida | Validador |
|---|---|---|---|---|
| 1 | 2026-09-07 al 2026-09-11 | v1 | [`corrida_1_semana_2026-09-07.md`](salidas/corrida_1_semana_2026-09-07.md) | 21/21 (spec v1) |
| 2 | 2026-09-14 al 2026-09-18 | v2 | [`corrida_2_semana_2026-09-14.md`](salidas/corrida_2_semana_2026-09-14.md) | 24/26 (spec v2) |
| 3 | 2026-09-21 al 2026-09-24 (8 de 10 archivos) | v3 | [`corrida_3_semana_2026-09-21.md`](salidas/corrida_3_semana_2026-09-21.md) | 28/29 (spec v3) |

Además, después de cada cambio de contrato se vuelve a correr la semana anterior con la versión nueva. Esa corrida extra no cuenta entre las tres y sirve para atribuir el cambio en la salida al cambio en el prompt y no a que cambiaron los datos.

### Corrida 1: contrato v1 sobre la semana 2026-09-07

**Cómo fue:** 29 turnos, 571 segundos, modelo `claude-sonnet-5`, 28 llamadas a herramientas (12 Read, 12 Grep, 3 Glob, 1 Write). Los datos completos están en [`salidas/corrida_1_semana_2026-09-07.md.meta.json`](salidas/corrida_1_semana_2026-09-07.md.meta.json). El agente respondió `salidas/corrida_1_semana_2026-09-07.md, 10/10`.

**Qué salió bien (verificado contra los textos de origen, no supuesto):**
- Estructura: el validador da 21/21. El máximo fue 32 palabras en un bullet, 17 en una celda y 1.010 palabras en total, contra límites de 35, 25 y 1.200.
- Cifras: contrasté 24 líneas de tablas de cierre (tipo de cambio, brecha, Cresud, Merval, LECAP, Profertil, Bioceres) y unas 25 afirmaciones de los dailys. Todo coincide con el texto de origen, salvo la etiqueta de fuente imprecisa de F5.
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
- **F4. Una fecha que no está en los informes (RETIRADA en el hito 7).** En la auditoría de la corrida 1 se afirmó que "Reunión del 16/9" era conocimiento externo porque ningún daily de la semana mencionaba esa fecha. **Fue un error de la auditoría:** el daily del miércoles dice "una probabilidad cercana al 60% a una suba de tasas de la Fed el 16 de septiembre". Las búsquedas de entonces no incluían esa formulación. Lo que había era una etiqueta de fuente imprecisa: la expectativa cita `[lun-daily]` y la fecha está en el del miércoles (es del tipo F5). Esta falla se mantuvo escrita como F4 en los hitos 3 a 6 y motivó en parte la iteración 2; después de retirarla, F4 se sostiene con otros ejemplos reales: afirmar más de lo que dice la fuente ("entre los sectores que más aportaron al PBI" en la corrida 2, cuando el daily dice "sobresalieron") y completar con un dato externo ("Después del 3/11" en la corrida 3, fecha que ningún daily da).
- **F5. Una etiqueta de fuente de más.** La expectativa 2 cita `[jue-daily] [lun-daily]`, pero el texto sobre "FX estable" y commodities está solo en el del jueves.

- **F6. Redacción con jerga, para lectores que no son especialistas.** El informe usa términos del mercado de capitales sin explicarlos. Un conteo mecánico da 18 términos distintos y 52 apariciones: `pbs` (6), `TEA` (5), `TNA` (4), `Treasury` (4), `intradía` (4), `BCRA` (3), `caución` (3), `A3500` (3) y seis montos escritos con "M", entre otros. Ejemplos textuales: "Caución cerca de 20% TNA", "TEA de la S13N6 de 27,56% a 28,08%", "la de 2027 pasó de TIR 4,6% a 4,2%". v1 solo pedía "tono neutro y profesional" y en el rol no decía que quien lee no es especialista. Sebastián aclaró después de ver la corrida 1 que los lectores no están familiarizados con conceptos técnicos. La lista de términos del conteo se armó después de ver esta corrida, a partir de la jerga observada y de la regla de estilo de v2; es una señal mecánica, no una prueba de claridad.

**Lectura:** el validador aprobó 21 de 21 y aun así hay seis fallas de fondo. Un chequeo de estructura no reemplaza leer el contenido contra las fuentes. Ninguna es una cifra mal copiada: son fallas de contrato (formato ambiguo, redacción sin destinatario claro, restricciones que no se cumplen) y de entorno.

**Decisión (tomada con Sebastián el 24/9):** la iteración 1 toca solo la pieza **Formato** y ataca F1 y F6, que son fallas de la forma de la salida: cómo se arma la tabla y cómo se escribe. F2 se corrige con un cambio de entorno y no de contrato (sección 3). F3, F4 y F5 son fallas de Restricciones y quedan para la iteración 2, que se confirma con lo que muestre la corrida 2. Una salvedad: la clase ubica el tono dentro de Restricciones; acá la redacción se incluyó en Formato porque define la forma de lo que se entrega y el pedido llegó junto con el cambio de la tabla. Es una decisión discutible y queda registrada.

### Corrida 2: contrato v2 sobre la semana 2026-09-14

**Cómo fue:** entorno aislado, 20 turnos, 203 segundos, modelo `claude-sonnet-5`; no abrió ningún archivo fuera de la semana (`fuera_de_la_semana: []`), así que F2 quedó resuelta. Metadatos en [`salidas/corrida_2_semana_2026-09-14.md.meta.json`](salidas/corrida_2_semana_2026-09-14.md.meta.json). Es la semana con el cierre del lunes en inglés.

**Qué salió bien (verificado contra los textos de origen):**
- Contrasté unas 30 afirmaciones: tasa de la Fed y su probabilidad, decisiones del Banco de Japón y del Banco de Inglaterra, riesgo país (485, 510, 515), reservas, Presupuesto 2027, fechas de la licitación, compras del Banco Central (123 y 169 millones), liquidación del agro, Cresud (precio y variación semanal), Treasury (4,99%, 5% y 4,92%), caución, Brent y los valores del dólar de ambos cierres, incluido el lunes en inglés. Todo coincide con las fuentes. Las 5 cifras que la herramienta marca como "no aparecen" son valores con un decimal en la fuente (`1.510,3`) que el agente completó con un cero (`1.510,30`).
- La "Reunión del 16/9" de la Fed está justificada: el daily del lunes dice "el miércoles" y el agente calculó la fecha. (En la semana A la fecha figuraba en el daily del miércoles; ver la retirada de F4 en la corrida 1.)
- **El cierre del lunes en inglés lo resolvió bien sin ninguna regla.** Anotó en el control de insumos "El cierre no incluye tablas de acciones", dejó `n/d` el precio inicial de Cresud y lo explicó en la sección 5. Las irregularidades que v1 y v2 no contemplaban a propósito no requirieron una regla.
- Jerga: 1 término distinto y 2 apariciones (`caución`).

**Qué falló:**
- **F3 se repite.** `mar_cierre`, `mie_cierre` y `jue_cierre` nunca se abrieron con Read (solo búsquedas), y aun así el control dice `| Martes | Sí | Sí | |` y "Insumos leídos: 10/10", sin observaciones. En la re-corrida de v2 sobre la semana A el agente sí lo aclaró ("Cierre consultado solo en dólar y Cresud"), así que el mismo contrato produce dos comportamientos distintos.
- **F7. "Tipo de dato" dice `n/d` cuando hay un valor.** La regla de v2 dice "`n/d` si no hay dato" y no aclara qué pasa cuando falta solo uno de los dos extremos: `| Tasa de EE.UU. a 10 años | n/d | 4,92% (dato del 17/9) | n/d | n/d |` y `| Acción de Cresud | n/d | $2.042,00 (dato del 18/9) | n/d | n/d |`.
- **F8. La regla de estilo de v2 generó una ambigüedad nueva.** v2 pide "puntos y no pbs". Para el riesgo país funciona, pero para las tasas de interés no: el informe dice "La Reserva Federal de EE.UU. subió la tasa 25 puntos, a 3,75%-4,00%" y "El Banco de Japón subiría la tasa 25 puntos, a 1,25%". Un lector no especialista puede entender que la tasa subió 25 puntos porcentuales, cuando la fuente habla de 25 puntos básicos, es decir 0,25 puntos porcentuales.
- **F9. Una contradicción dentro del mismo informe.** La tabla 4.1 dice sobre Cresud "Sin precio inicial no se puede evaluar el cambio de la semana", y la sección 4.2 dice "Cresud (empresa agro) subió 4,9% en la semana [vie-cierre]". El cierre del viernes trae la variación semanal, pero v2 obliga a `n/d` en "Cambio" si no hay dos valores de cierre.
- Residuales: una viñeta de 44 palabras en la sección 5 (límite 35) y una paráfrasis más fuerte que la fuente: el informe dice que el agro está "entre los sectores que más aportaron al PBI", pero el daily dice que "sobresalieron" Pesca, Minería y Agro por su crecimiento y no habla de aporte.

### Corrida 3: contrato v3 sobre la semana 2026-09-21 (lunes a jueves)

**Cómo fue:** entorno aislado, 23 turnos, 301 segundos, modelo `claude-sonnet-5`, 8 archivos leídos completos y ninguno fuera de la semana. Metadatos en [`salidas/corrida_3_semana_2026-09-21.md.meta.json`](salidas/corrida_3_semana_2026-09-21.md.meta.json). **La semana estaba incompleta:** los informes del viernes 25/9 no existían todavía (la corrida se hizo el jueves 24/9 a la noche), así que el agente recibió 8 de 10 archivos. Validador: 28/29 (solo falla la jerga: `caución`).

**Qué salió bien (verificado contra los textos de origen):**
- **Manejó la semana incompleta sin ninguna regla para eso.** Control de insumos: `| Viernes | No | No | No existen vie_daily.txt ni vie_cierre.txt en la carpeta; no se consultaron. |` e "Insumos leídos: 8/10". En la sección 5 avisó que "Fin de semana" y "Cambio" quedan `n/d` y que las expectativas con fecha 25/9 quedan sin evidencia.
- Detectó una inconsistencia real en los dailys: el del jueves dice que el WTI "avanzó 2,2% hasta US$92,5" y el del miércoles lo tenía en 94,6, lo que sería una baja.
- Contrasté unas 30 afirmaciones de los dailys y 12 líneas de tablas de cierre: coinciden (riesgo país 524 y 557, Treasury 5,11%, canje de US$3.332 millones, vencimientos de $13,6 a $8,6 billones, pago de US$793 millones al FMI, reservas netas de US$7.568 millones, posición vendida de US$485 a US$278 millones, letra de noviembre en 26,57% y 26,74%, entre otras). Las dos cifras que la herramienta marca son Cresud con un cero de más.

**Qué falló:**
- **F4 (sigue): un dato externo.** La expectativa 4 dice "Después del 3/11". Ningún daily de la semana da esa fecha; el del miércoles dice que el acuerdo con Irán "podría llegar después de las elecciones". Es exactamente lo que la regla de v3 prohíbe.
- **F11 (nueva): sin una regla para semanas incompletas, la tabla 4.1 queda sin variaciones.** "Fin de semana", "Cambio" y "Tipo de dato" dicen `n/d` en las diez filas, con el último dato entre paréntesis, aunque hay cierres del lunes y del jueves. Hay 36 `n/d` en el informe, contra 8 a 11 en las semanas completas. El resumen sí cuenta los movimientos ("el financiero subió de $1.597 a $1.614"), pero el lector que mira la tabla no ve ningún cambio.
- **F10 (sigue).** "Tasas de interés en pesos" salió esta vez de la letra a tasa fija de noviembre (26,57%), no de la caución del daily como en las otras semanas: es la tercera versión de esa fila.
- **Jerga que el validador no ve.** Además de `caución`, la expectativa 7 habla de "la posición vendida del Banco Central en dólar futuro" y la 3 del "saldo expuesto" tras el "canje"; ninguno está en la lista mecánica.

## 5. Iteración 1

- **Qué falló (textual):** F1 y F6 de la corrida 1. Las dos citas más claras: `| Petróleo (Brent) | 97,3 (intradía) | 104,7 (intradía) | +7,6% |` (columnas de "Cierre" con cotizaciones de la mañana) y "Caución cerca de 20% TNA; TEA de la S13N6 de 27,56% a 28,08%" (jerga sin explicar). Medición del antes: 18 términos técnicos distintos y 52 apariciones.
- **Pieza del contrato que toqué:** Formato (sección 5 de `system_prompt.md`). Además, como el formato cambió, se actualizaron dos ejemplos de la sección 6 que mostraban el formato viejo (la fila de la tabla 4.1 y el bullet del resumen con "pbs"). Es una consecuencia directa, no una mejora de los ejemplos. El user prompt no cambió.
- **Cambio (antes → después):** las versiones completas están congeladas en [`iteraciones/v1/`](iteraciones/v1/system_prompt.md) y [`iteraciones/v2/`](iteraciones/v2/system_prompt.md).

  Antes (v1), tabla 4.1:
  ```
  ### 4.1 Variables macro
  | Variable | Cierre lunes | Cierre viernes | Cambio | Lectura para el agro | Fuente |
  (diez filas fijas: Dólar mayorista (A3500); Dólar CCL; Brecha CCL; Dólar MEP; Tasas en pesos; Riesgo país;
   Treasury 10 años; Petróleo (Brent); Compras del BCRA y liquidación del agro; Acción Cresud (CRES))
  ```
  Después (v2):
  ```
  ### 4.1 Variables económicas
  | Variable | Inicio de semana | Fin de semana | Cambio | Tipo de dato | Lectura para el agro | Fuente |
  (diez filas fijas: Dólar oficial (mayorista); Dólar financiero (CCL); Brecha entre dólar financiero y oficial;
   Dólar bolsa (MEP); Tasas de interés en pesos; Riesgo país; Tasa de EE.UU. a 10 años; Petróleo (Brent);
   Compras del Banco Central y dólares del agro; Acción de Cresud)
  ```
  Se agregaron dos bloques nuevos dentro de Formato:
  - **Cómo se completa la tabla 4.1:** "Inicio/Fin de semana" es el valor del cierre si la variable está en las tablas de cierre y, si solo está en los dailys, el último valor que cita el daily con su fecha. "Tipo de dato" solo puede ser `Cierre`, `Daily`, `Mixto` o `n/d`. "Cambio" se calcula solo cuando el tipo es `Cierre`; en cualquier otro caso, `n/d`.
  - **Cómo se escribe:** el lector trabaja en el agro y no es especialista en finanzas; frases cortas y una idea por frase; reemplazar la jerga por palabras comunes con ejemplos (Banco Central y no BCRA, puntos y no pbs, tasa de interés anual y no TEA o TNA, renovación de deuda y no rollover, durante el día y no intradía); explicar entre paréntesis lo que no se pueda reemplazar; montos con unidad y sin "M".
- **Qué espero ver, y qué podría salir mal:** en el validador (spec v2), F1 y F6 en cero. El riesgo principal es que las variables que solo salen de los dailys queden sin cambio numérico (`n/d`), lo que es más honesto pero menos informativo, y que explicar los términos alargue el texto hasta el límite de 1.200 palabras.
- **Qué cambió en la salida:** para separar el efecto del contrato del efecto del aislamiento, se compararon dos corridas sobre **los mismos datos (semana 2026-09-07) y el mismo entorno aislado**: un control con v1 y una re-corrida con v2. Ambas están en [`iteraciones/v2/`](iteraciones/v2/) con sus metadatos. La corrida 1 original, que no estaba aislada, se muestra aparte.

  | | Corrida 1 (v1, sin aislar) | Control (v1, aislado) | Re-corrida (v2, aislado) |
  |---|---|---|---|
  | Jerga: términos distintos / apariciones | 18 / 52 | 12 / 26 | **1 / 1** |
  | Chequeos de la spec v2 aprobados | 22/26 | 22/26 | **25/26** |
  | Filas de la tabla 4.1 con datos de daily y "Cambio" numérico | 1 | 2 | **0** |
  | Columna "Tipo de dato" | no existe | no existe | en las 10 filas |
  | Palabras (límite 1.200) | 1.010 | 928 | 1.110 |
  | Archivos leídos completos (de 10), medido con la cobertura de lectura | 7 | 7 | 7 |

  Antes y después de F1, misma variable y mismos datos:
  - Control (v1): `| Petróleo (Brent) | US$97,3 (apertura del lunes) | US$104,7 (dato del viernes, no cierre) | +7,6% aprox. |`. El agente ya avisaba de que no eran cierres, pero igual calculaba el cambio.
  - Re-corrida (v2): `| Petróleo (Brent) | US$97,3 (dato del 7/9) | US$104,7 (dato del 11/9) | n/d | Daily |`.

  Antes y después de F6, misma idea:
  - Control (v1): "Las tasas en pesos siguieron cerca de 20% TNA y el Tesoro salió a renovar $8,1 billones con instrumentos cortos" y "El riesgo país figuraba en 490 pbs el lunes".
  - Re-corrida (v2): "Las tasas en pesos siguieron cerca de 20% anual y el Tesoro ofreció solo instrumentos cortos en su licitación del viernes" y "El riesgo país (costo de financiar al país en dólares) era de 490 puntos el 4/9".

  **Lo que no salió como se esperaba:** (a) el texto creció de 928 a 1.110 palabras, cerca del límite de 1.200, como se había previsto; (b) la corrida 2 mostró tres defectos nuevos (F7, F8, F9), y los tres son consecuencia de reglas que agregó v2. Una salvedad general: cada condición se corrió una sola vez, así que la variación entre corridas de un mismo contrato no está medida.

  **Corrección posterior (hito 6).** En este punto se había escrito que el control con v1 había abierto todos los archivos y que v2 dejaba 3 cierres sin abrir, y se había sugerido que podía ser un efecto de v2. Fue un error de medición: el script solo registraba qué archivos se abrieron, no cuánto de cada uno. Al medir la cobertura de lectura (líneas leídas de cada archivo) sobre los logs de las cuatro corridas, el patrón es idéntico en todas: **7 de 10 archivos leídos completos** (los cinco dailys y dos cierres) y tres cierres sin leer o casi sin leer. En el control con v1, `mar_cierre`, `mie_cierre` y `jue_cierre` figuraban como abiertos, pero de cada uno se leyeron 6 líneas de unas 1.740. F3 no depende de la versión del contrato.
- **Commit:** contrato v2 en `0e49579`; evidencia y corrida 2 en el commit del hito 5.

## 6. Iteración 2

**Decisión (tomada con Sebastián el 24/9).** Se plantearon dos opciones. A: tocar **Restricciones** para F3, F4, F5, F8 y F9. B: volver a tocar **Formato** para F7, F8 y F9. Se eligió A porque casi todo lo abierto es "el agente hace algo que no debería o declara algo que no cumplió", y porque F8 (la más seria para el lector) se puede expresar como una prohibición. F7 queda abierta y documentada. Riesgo asumido de A: la regla de las tasas choca con la regla de estilo de v2 ("puntos y no pbs", en Formato). Para no tocar una segunda pieza, la propia regla nueva dice que prevalece sobre la de estilo.

- **Qué falló (textual):**
  - F3: `| Martes | Sí | Sí | |` con `mar_cierre` sin abrir, y "Insumos leídos: 10/10". Cobertura medida en las cuatro corridas: 7 de 10 archivos completos.
  - F4: la paráfrasis "entre los sectores que más aportaron al PBI" cuando la fuente dice "sobresalieron" (corrida 2). El ejemplo de la fecha de la Fed que figuraba acá fue un error de auditoría, retirado en el hito 7 (la fecha estaba en el daily del miércoles); ver la corrida 1.
  - F5: `[jue-daily] [lun-daily]` cuando el texto citado está solo en el del jueves.
  - F8: "La Reserva Federal de EE.UU. subió la tasa 25 puntos, a 3,75%-4,00%", que es un cuarto de punto porcentual.
  - F9: "Sin precio inicial no se puede evaluar el cambio de la semana" en la tabla y "Cresud (empresa agro) subió 4,9% en la semana" en 4.2.
- **Pieza del contrato que toqué:** Restricciones (sección 4 de `system_prompt.md`). Formato, Ejemplos y user prompt no cambiaron. La diferencia entre [`iteraciones/v2/`](iteraciones/v2/system_prompt.md) y [`iteraciones/v3/`](iteraciones/v3/system_prompt.md) son exactamente cinco líneas nuevas.
- **Cambio (antes → después):** antes, la sección 4 tenía 9 reglas. Después, tiene 14; se agregaron:
  - **Control de insumos:** marcar "Sí" solo si leyó el archivo de principio a fin (aunque sea en varios tramos); si solo lo consultó con búsquedas o leyó una parte, "No" y aclararlo en Observaciones; "Insumos leídos" cuenta solo los "Sí".
  - **Fechas, plazos y cifras:** solo si figuran en los informes o se deducen directamente de algo que figura (con el ejemplo de "el miércoles" dicho un lunes 14); sin completar con el calendario; sin afirmar más de lo que dice la fuente.
  - **Fuentes:** cada etiqueta `[día-tipo]` apunta a un archivo donde figura lo que se afirma; sin etiquetas "por las dudas".
  - **Tasas de interés:** no escribir "puntos" a secas para el cambio de una tasa; escribir "puntos porcentuales" con el valor real (0,25 y no 25). Prevalece sobre la regla de estilo de Formato.
  - **Coherencia:** el informe no se contradice; si un dato figura en una sección, otra no puede decir que falta o que no se puede calcular.
- **Cómo se mide el después.** Con [`scripts/validar_salida.py --spec v3`](scripts/validar_salida.py), que agrega tres chequeos mecánicos: el "Insumos leídos" coincide con la cantidad de "Sí"; cada "Sí" es un archivo que el agente leyó completo (usa la cobertura de lectura que ahora guarda el `.meta.json`); y no hay "N puntos" a secas para tasas de interés (heurística). Sobre la corrida 2 (v2), el validador v3 da 25/29 y detecta exactamente F3 y F8. Las reglas de fechas, fuentes y coherencia no se pueden chequear con un script: se revisan a mano contra los insumos.
- **Qué espero ver, y qué podría salir mal:** F8 en cero. Para F3, una de dos: el agente lee los diez archivos completos (más lento y más caro) o marca "No" en los cierres que no leyó y declara 7/10; cualquiera de las dos es coherente. Riesgos: que el agente ignore la regla de las tasas por la de estilo, y que para cumplir la de coherencia quite información en lugar de reconciliarla.
- **Qué cambió en la salida:** se compararon cuatro corridas sobre **los mismos datos (semana 2026-09-14) y el mismo entorno aislado**: dos con v2 (la corrida 2 y una repetición) y dos con v3 (a y b). Las cuatro están en [`salidas/`](salidas/corrida_2_semana_2026-09-14.md) e [`iteraciones/v3/`](iteraciones/v3/) con sus metadatos. Con dos observaciones por condición se ve cuánto varía cada contrato consigo mismo.

  | | v2 · corrida 2 | v2 · repetición | v3 · a | v3 · b |
  |---|---|---|---|---|
  | Chequeos de la spec v3 | 25/29 | 25/29 | **28/29** | **28/29** |
  | "Sí" en cierres sin lectura completa (F3) | 3 | 3 | **0** | **0** |
  | Archivos leídos completos (de 10) | 7 | 7 | **10** | **10** |
  | "25 puntos" a secas para tasas (F8) | 4 | 3 | **0** | **0** |
  | "0,25 puntos porcentuales" | 0 | 0 | 3 | 3 |
  | Contradicción Cresud tabla / 4.2 (F9, revisión a mano) | sí | sí | **no** | **no** |
  | Jerga: términos distintos / apariciones | 1 / 2 | 1 / 1 | 1 / 1 | 1 / 1 |
  | Palabras (límite 1.200) | 1.057 | 1.095 | 967 | 1.107 |
  | Turnos / segundos / tokens de salida | 20 / 203 / 21k | 19 / 184 / 20k | 28 / 446 / 52k | 27 / 316 / 36k |

  Antes y después, misma idea:
  - **F8.** v2: "La Reserva Federal de EE.UU. subió la tasa 25 puntos, a 3,75%-4,00%". v3: "La Reserva Federal (Fed, banco central de EE.UU.) subió su tasa de referencia 0,25 puntos porcentuales, hasta un rango de 3,75%-4,00%". La misma corrección apareció en las expectativas: "Japón subió 0,25 puntos porcentuales".
  - **F3.** v2: `| Martes | Sí | Sí | |` con `mar_cierre` sin abrir. v3: el agente hizo 24 lecturas y abrió los diez archivos de principio a fin en las dos corridas, de modo que cada "Sí" está respaldado. La regla admitía también marcar "No" y declarar 7/10; ninguna de las dos corridas eligió esa vía.
  - **F4.** v2: el agro "entre los sectores que más aportaron al PBI". v3: "entre los sectores que sobresalieron junto con pesca (+44,7%) y minería (+16,4%)", que es lo que dice la fuente. Las fechas ("el miércoles 16/9") se dedujeron de un dato que figura en el daily, como pedía la regla.
  - **F9.** v2: la tabla dice "Sin precio inicial no se puede evaluar el cambio de la semana" y 4.2 dice "subió 4,9% en la semana". v3: ninguna de las dos corridas se contradice.
  - **F5.** No hay una medición mecánica. En la revisión a mano no aparecieron etiquetas de fuente de más en las corridas con v3.

  **Verificación de contenido de las corridas con v3:** todas las cifras específicas que la herramienta no encuentra son valores con un decimal menos en la fuente (`1.510,3`, `2.042,0`) que el agente completó con un cero. Las afirmaciones dudosas se revisaron a mano contra los textos y coinciden (por ejemplo "agosto de 2016" para el récord de urea, "supuestos macroeconómicos un tanto exigentes", Merval en 1.886,1, Cresud en 1.890,0, "dos subas en 2027" según los futuros).

  **Lo que no salió como se esperaba:**
  - **El costo subió.** Leer los diez archivos completos duplicó el tiempo (de 184-203 a 316-446 segundos) y casi duplicó los tokens de salida. La corrección de F3 se pagó con más cómputo; la alternativa (marcar "No" y declarar 7/10) habría salido más barata.
  - **La regla de coherencia se cumplió quitando información.** Era el riesgo que se había anotado antes de correr. La variación semanal de Cresud (+4,9%), que el cierre del viernes trae, desapareció de las dos corridas con v3 en lugar de reconciliarse con la tabla: F9 se eliminó, pero se perdió un dato.
  - **F7 sigue.** "Tipo de dato" dice `n/d` cuando hay un valor en 3 de las 4 corridas (2 filas en cada una, salvo v3·b). No era objetivo de esta iteración.
  - **Jerga residual.** `A3500` aparece una vez en la sección 5 de las dos corridas con v3, y la v3·a agrega la sigla "BCS", que no está en la lista del validador.
  - **F10, nueva y abierta: la tabla 4.1 no define qué serie usar.** El cierre trae varias series para la misma variable y cada corrida elige una. Sobre los mismos datos, en las cuatro corridas: "Dólar oficial" usó `BCRA 3500` en tres y el dólar *spot* en una (variación de +0,1% contra +0,5%); "Dólar bolsa (MEP)" usó la serie con GD30 en tres y con AL30 en una; "Tasas en pesos" salió de la caución del daily en tres y de un gráfico del cierre en una; "Compras del Banco Central" fue el acumulado del mes en tres y la compra diaria en una. Dos de las cuatro corridas se apartan del criterio mayoritario en dos filas cada una. Es una falla de repetibilidad, el criterio que más pesa después de la especificación, y las reglas de Restricciones de v3 no la tocan. Queda como limitación conocida y como siguiente paso natural sobre la pieza Formato.

  **Salvedades:** dos observaciones por condición y una sola semana. Que v3 funcione en la semana del 14 no prueba que funcione en la del 21; eso lo mide la corrida 3.
- **Commit:** contrato v3 en `f4c30b8`; evidencia en el commit del hito 6b.

## 7. Comparación de las tres corridas

Las tres corridas de la consigna usan **tres versiones distintas del contrato**, por diseño: cada una se corrió después de una iteración. Por eso no son tres repeticiones de lo mismo y no deben leerse así. La evidencia de repetibilidad está en las corridas que comparten versión (segunda tabla).

**Las tres corridas oficiales:**

| | Corrida 1 | Corrida 2 | Corrida 3 |
|---|---|---|---|
| Semana | 7 al 11/9 | 14 al 18/9 | 21 al 24/9 (8 de 10 archivos) |
| Contrato | v1 | v2 | v3 |
| Validador con la spec de su propia versión | 21/21 | 24/26 | 28/29 |
| Validador con la spec vigente (v3) | 24/29 | 25/29 | 28/29 |
| Archivos leídos completos | 7 de 10 | 7 de 10 | 8 de 8 |
| Jerga mecánica (siglas): términos / apariciones | 18 / 52 | 1 / 2 | 1 / 1 |
| Términos técnicos amplios (33 términos): distintos / apariciones | 16 / 33 | 11 / 18 | 16 / 24 |
| Palabras / etiquetas de fuente | 1.010 / 69 | 1.057 / 53 | 1.070 / 49 |

**Repetibilidad con el mismo contrato (v3), cuatro salidas sobre tres semanas distintas:**

| Semana | Validador (spec v3) | Palabras | Etiquetas de fuente | `n/d` | Archivos completos | Segundos |
|---|---|---|---|---|---|---|
| 7/9 | 28/29 | 1.117 | 49 | 8 | 10 de 10 | 374 |
| 14/9 (a) | 28/29 | 967 | 54 | 11 | 10 de 10 | 446 |
| 14/9 (b) | 28/29 | 1.107 | 51 | 9 | 10 de 10 | 316 |
| 21/9 | 28/29 | 1.070 | 49 | 36 | 8 de 8 | 301 |

**Qué se mantuvo fijo.** En las cuatro salidas con v3: los siete títulos en el mismo orden, el control de insumos de cinco días, las diez variables de la tabla 4.1 con los mismos nombres y orden, los valores permitidos de "Estado al viernes" y "Tipo de dato", entre 25 y 26 filas de tabla y entre 967 y 1.117 palabras. Las cuatro dan 28/29 y fallan el mismo chequeo (una sigla residual de la lista de jerga). Que las columnas y las diez filas fijas sean idénticas semana tras semana es lo que permite comparar un informe con el siguiente.

**Qué varió.**
- **La serie que se elige en algunas filas (F10).** El cierre trae varias series para la misma variable (dólar oficial de referencia o *spot*, MEP con GD30 o con AL30, tasa del daily o de un gráfico o una letra) y cada corrida elige una. Es la principal falla de repetibilidad que queda.
- **"Tipo de dato: `n/d`" con un valor cargado (F7):** aparece o no según la corrida.
- **Semana incompleta (F11):** la corrida 3 tiene 36 `n/d` contra 8 a 11.
- **Costo:** de 184-203 segundos con v2 a 301-446 con v3, por leer los diez archivos completos.
- **Cantidad de expectativas:** entre 6 y 8 filas.

**Cómo leer el indicador de jerga.** La lista mecánica cuenta siglas y códigos (`pbs`, `TEA`, `TNA`, `TIR`, `BCRA`, `A3500`, ...) y bajó de 52 apariciones a 1: v2 y v3 eliminaron las siglas. Pero un lector no especialista no se traba solo con siglas, sino con conceptos: brecha, CCL, MEP, Brent, Merval, licitación, canje, posición vendida. Con una lista amplia de 33 términos, la baja es mucho menor: de 33 apariciones en la corrida 1 a 24-28 con v3. El texto quedó más claro, pero sigue siendo un informe de analista y no un informe para clientes que no conocen el mercado.

## 8. Reflexión: qué aprendí del contrato

1. **Decir para quién se escribe es tan importante como decir qué se escribe.** v1 tenía rol, tarea y formato, pero no decía que quien lee no es especialista, y produjo un texto para analistas (F6: 18 términos técnicos, 52 apariciones). Una sola instrucción sobre el lector y ejemplos de reemplazo de jerga cambiaron el resultado más que cualquier otra regla.
2. **Una pieza por vez sirve, pero las reglas interactúan.** La regla de estilo de v2 ("puntos y no pbs") funcionaba para el riesgo país y produjo "la tasa subió 25 puntos" para las tasas de interés, que es una lectura equivocada (son 0,25 puntos porcentuales). Corregirla obligó a escribir una regla en otra pieza, con una cláusula que dice cuál prevalece. Cada regla nueva puede romper una anterior.
3. **Un validador no es una evaluación.** La corrida 1 dio 21/21 y tenía seis fallas de fondo. Además, el indicador de jerga bajó de 52 a 1 y sobrestima la mejora real de claridad. Los chequeos mecánicos sirven para lo que se puede medir (estructura, valores permitidos) y dan falsa seguridad si se los toma por calidad.
4. **La medición también se equivoca, y hay que corregirla a la vista.** Dos conclusiones de este trabajo eran erróneas y se retiraron: que v2 dejaba cierres sin abrir (el script no medía cuánto se leía de cada archivo) y que una fecha de la Fed era conocimiento externo (las búsquedas de la auditoría no encontraron una frase que sí estaba). Lo que las detectó fue guardar los registros de cada corrida y medir de nuevo con otro instrumento.
5. **Una sola corrida engaña.** Repetir una condición mostró qué era estable (F3 y F8 con v2, en las dos corridas) y qué era variabilidad genuina (la serie elegida en cada fila, F10). Aislar el entorno y comparar con los mismos datos evitó atribuir al contrato lo que era del entorno.
6. **No toda irregularidad necesita una regla, pero todo hueco de especificación produce variación.** El cierre del lunes en inglés y la semana sin viernes los resolvió el agente sin ninguna instrucción, avisando lo que faltaba. En cambio, no decir qué serie usar en cada fila (F10) o qué hacer con una semana incompleta (F11) generó respuestas distintas.
7. **Ser honesto cuesta.** Pedirle que cuente como leído solo lo que leyó completo lo llevó a leer los diez archivos, y eso duplicó el tiempo. Cada exigencia de fiabilidad tiene un precio en cómputo, y a veces la solución más barata (declarar 7 de 10) era también válida.
8. **El límite: el resultado es de analista, no de cliente.** Que el contrato cumpla su especificación no quiere decir que sirva para cualquier lector. Para clientes finales habría que cambiar la audiencia de fondo (secciones, extensión, un mensaje central, explicación de cada concepto), es decir, escribir otro contrato. Y quedan abiertas F10 (qué serie usar) y F11 (semanas incompletas) como candidatas a la siguiente iteración.

## 9. Nota sobre los datos

Los informes originales (mails y PDF) no se publican en este repositorio: `insumos/` y los archivos `.pdf`, `.eml` y `.msg` están excluidos por `.gitignore`. Solo se publican los prompts, las salidas, los scripts y este README.

## 10. Dónde está cada resumen

| Semana | Corrida oficial de la consigna (`salidas/`) | Misma semana con el contrato final (v3) |
|---|---|---|
| 7 al 11/9 | [`corrida_1_semana_2026-09-07.md`](salidas/corrida_1_semana_2026-09-07.md), con v1 | [`evidencia_semana_2026-09-07_con_v3.md`](iteraciones/v3/evidencia_semana_2026-09-07_con_v3.md) |
| 14 al 18/9 | [`corrida_2_semana_2026-09-14.md`](salidas/corrida_2_semana_2026-09-14.md), con v2 | [`evidencia_semana_2026-09-14_con_v3_b.md`](iteraciones/v3/evidencia_semana_2026-09-14_con_v3_b.md) (hay otra: [`_a`](iteraciones/v3/evidencia_semana_2026-09-14_con_v3_a.md)) |
| 21 al 24/9 | [`corrida_3_semana_2026-09-21.md`](salidas/corrida_3_semana_2026-09-21.md), con v3, 8 de 10 archivos | es la misma |

Las corridas de la columna derecha para las semanas del 7 y del 14 son corridas extra hechas como evidencia de las iteraciones; no son parte de las tres que pide la consigna. Las demás corridas de evidencia (control con v1, repetición con v2) están en [`iteraciones/v2/`](iteraciones/v2/) e [`iteraciones/v3/`](iteraciones/v3/).

## 11. Cómo se hizo este trabajo

Las decisiones de diseño (qué tarea, qué formato, qué pieza iterar y cuándo) las tomó Sebastián Maya. Un asistente de IA (Claude, dentro de Claude Code) escribió y corrió los scripts, ejecutó al agente, auditó las salidas contra los informes y redactó este README a partir de esas decisiones y de los registros de cada corrida. El agente que produce los informes usa el modelo `claude-sonnet-5`. Los prompts de `iteraciones/v1/`, `v2/` y `v3/` son las versiones tal como se corrieron, congeladas antes de cada corrida.
