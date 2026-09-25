# User prompt: pedido de la semana

Este archivo es la plantilla del pedido puntual. Antes de cada corrida se reemplazan los cuatro valores entre llaves dobles; los valores usados en cada corrida están en el README.

## 2. Contexto (variable de esta corrida)
- Semana a analizar: del lunes {{LUNES}} al viernes {{VIERNES}}.
- Carpeta de insumos: `insumos/semana_{{LUNES}}/` (diez archivos: `lun`, `mar`, `mie`, `jue`, `vie` seguidos de `_daily.txt` o `_cierre.txt`).
- Versión del contrato: {{VERSION}}
- Archivo de destino: `salidas/{{ARCHIVO}}`

## 3. Tarea
Leé los diez archivos de la semana y escribí el informe semanal con el formato definido en tus instrucciones. Guardalo en el archivo de destino con la herramienta de escritura, y en la línea `Contrato:` del informe poné la versión indicada arriba.

Cuando termines, respondé solo con la ruta del archivo guardado y la cantidad de insumos que leíste (por ejemplo: `salidas/ejemplo.md, 10/10`).
