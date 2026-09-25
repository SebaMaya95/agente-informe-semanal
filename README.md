# Agente de informe semanal: mercado y sector agro

> **Estado:** en construcción. Hito 1 de 7 (estructura). Cada sección marcada como _pendiente_ se completa en el hito que corresponde, justo después de cada corrida y no al final, para que el registro no dependa de la memoria.

## 1. La tarea

_Pendiente: una frase inequívoca._

Borrador: cada semana, un agente lee los 5 informes _daily_ (lunes a viernes) y los 5 informes de _cierre de día_ (lunes a viernes) y produce un informe semanal estructurado con (a) el resumen de la semana, (b) qué se esperaba en cada daily frente a lo que mostró cada cierre, (c) señales para la semana siguiente y (d) un apartado sobre lo que puede afectar al sector agro, desde lo macro (dólar, tasas) hasta lo sectorial.

## 2. El contrato: las seis piezas

| Pieza | Va en | Archivo | Estado |
|---|---|---|---|
| 1. Rol | system | `system_prompt.md` | pendiente |
| 2. Contexto | system (estable) + user (variable) | ambos | pendiente |
| 3. Tarea | user | `user_prompt.md` | pendiente |
| 4. Restricciones | system | `system_prompt.md` | pendiente |
| 5. Formato | system | `system_prompt.md` | pendiente |
| 6. Ejemplos | system | `system_prompt.md` | pendiente |

## 3. Cómo se corre

Paso 0, manual y fuera del contrato: los informes llegan por mail (texto de introducción en el cuerpo y el informe completo en PDF), se descargan y se ubican en `insumos/<semana>/`. Esa carpeta **no se publica** (ver sección 9).

_Pendiente: convención de nombres de archivos y cómo se invoca al agente._

## 4. Corridas

| Corrida | Semana | Versión del contrato | Salida |
|---|---|---|---|
| 1 | _pendiente_ | v1 | _pendiente_ |
| 2 | _pendiente_ | v2 | _pendiente_ |
| 3 | _pendiente_ | v3 | _pendiente_ |

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

Los informes originales (mails y PDF) no se publican en este repositorio: `insumos/` y los archivos `.pdf`, `.eml` y `.msg` están excluidos por `.gitignore`. Solo se publican los prompts, las salidas y este README.
