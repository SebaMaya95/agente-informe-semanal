"""Ayuda para la revisión de contenido: lista las cifras de un informe que NO aparecen en los
insumos de la semana. Sirve para saber dónde mirar, no reemplaza leer el informe.

Uso, desde la raíz del repo (los insumos existen solo en la máquina de quien corre el agente):
    python scripts/chequear_cifras.py salidas/corrida_2_semana_2026-09-14.md 2026-09-14

Qué hace: extrae cada número del informe (sin fechas, etiquetas de fuente ni numeración) y lo
busca como texto en los .txt de esa semana. Los que no están suelen ser cifras calculadas por el
agente (cambios porcentuales, diferencias, sumas), que hay que recalcular a mano, o cifras
redondeadas; y, a veces, una cifra inventada. Un número que sí aparece solo prueba que existe en
algún lugar de los insumos, no que corresponda a la variable correcta.
"""
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

NUM = re.compile(r"(?<![\w.,/-])[+-]?\d[\d.]*(?:,\d+)?")


def numeros(texto):
    texto = "\n".join(l for l in texto.splitlines() if not l.lstrip().startswith("#"))  # sin títulos (4.1, 4.2...)
    limpio = re.sub(r"\[(?:lun|mar|mie|jue|vie)-(?:daily|cierre)\]", " ", texto)
    limpio = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", limpio)             # fechas ISO
    limpio = re.sub(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b", " ", limpio)   # fechas 7/9, 10/10
    limpio = re.sub(r"^\s*\|?\s*\d{1,2}\s*\|", " ", limpio, flags=re.M)  # numeración de tablas
    out = []
    for m in NUM.finditer(limpio):
        t = m.group(0).lstrip("+-")
        digitos = re.sub(r"\D", "", t)
        if len(digitos) <= 1 or t in ("2026", "1200"):
            continue
        out.append(t)
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    informe, lunes = sys.argv[1], sys.argv[2]
    carpeta = os.path.join("insumos", f"semana_{lunes}")
    fuentes = ""
    for f in sorted(glob.glob(os.path.join(carpeta, "*.txt"))):
        fuentes += open(f, encoding="utf-8").read() + "\n"
    if not fuentes:
        sys.exit(f"No hay .txt en {carpeta}")
    texto = open(informe, encoding="utf-8").read()
    todos = numeros(texto)
    unicos = list(dict.fromkeys(todos))
    # Las cifras de menos de tres dígitos (0,5; 3,5; 12) aparecen por casualidad en cualquier texto:
    # que estén no prueba nada, así que no se chequean.
    especificas = [t for t in unicos if len(re.sub(r"\D", "", t)) >= 3]
    cortas = len(unicos) - len(especificas)
    faltan = [t for t in especificas if not re.search(r"(?<![\d.,])" + re.escape(t) + r"(?!\d)", fuentes)]
    print(f"{informe}: {len(unicos)} cifras distintas; {len(especificas)} específicas (3 o más dígitos) y {cortas} cortas sin chequear.")
    print(f"De las específicas, {len(especificas) - len(faltan)} aparecen en los insumos y {len(faltan)} no.")
    print("No aparecen (calculadas, redondeadas o a revisar a mano):")
    print("  " + ", ".join(faltan) if faltan else "  ninguna")


if __name__ == "__main__":
    main()
