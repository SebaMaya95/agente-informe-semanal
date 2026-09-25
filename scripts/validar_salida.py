"""Valida que una salida respete el formato definido en system_prompt.md (sección 5).

Uso, desde la raíz del repo:
    python scripts/validar_salida.py salidas/corrida_1_....md [salidas/otra.md ...]

Chequea estructura, no calidad del análisis: títulos y orden, columnas de las tablas,
cantidad de filas, valores permitidos, fuentes en cada afirmación, extensión y que no
aparezca el nombre de la entidad que produce los informes. Sale con código 1 si algo falla.
"""
import os
import re
import sys

ENCABEZADOS = [
    "## 1. Control de insumos",
    "## 2. Resumen de la semana",
    "## 3. Expectativas explícitas",
    "## 4. Apartado agro",
    "### 4.1 Variables macro",
    "### 4.2 Sector agro específico",
    "## 5. Límites de esta síntesis",
]
CAB_S1 = ["Día", "Daily", "Cierre", "Observaciones"]
CAB_S3 = ["#", "Expectativa", "Dónde", "Horizonte", "Estado al viernes", "Evidencia"]
CAB_S41 = ["Variable", "Cierre lunes", "Cierre viernes", "Cambio", "Lectura para el agro", "Fuente"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
VARIABLES = [
    "Dólar mayorista (A3500)", "Dólar CCL", "Brecha CCL", "Dólar MEP", "Tasas en pesos",
    "Riesgo país", "Treasury 10 años", "Petróleo (Brent)",
    "Compras del BCRA y liquidación del agro", "Acción Cresud (CRES)",
]
ESTADOS = {"Cumplida", "No cumplida", "Abierta", "Sin evidencia"}
SIN_EXPECTATIVAS = "Sin expectativas explícitas en los informes de esta semana."
SIN_SECTOR = "Sin información sectorial en los informes de esta semana."
SIN_OBS = "Sin observaciones."
MAX_PALABRAS = 1200
# Términos que no pueden aparecer en la salida (el nombre de la entidad que produce los informes).
# La lista no se publica: vive en insumos/terminos_prohibidos.txt, un término por línea.
RUTA_PROHIBIDAS = os.path.join("insumos", "terminos_prohibidos.txt")
TAG = re.compile(r"\[(lun|mar|mie|jue|vie)-(daily|cierre)\]")


def secciones(texto):
    """Devuelve {encabezado: contenido} y la lista de encabezados encontrados, en orden."""
    lineas = texto.splitlines()
    marcas = []
    for i, l in enumerate(lineas):
        s = l.strip()
        if s in ENCABEZADOS:
            marcas.append((i, s))
    out = {}
    for n, (i, h) in enumerate(marcas):
        fin = marcas[n + 1][0] if n + 1 < len(marcas) else len(lineas)
        # 4. Apartado agro llega hasta 4.1; el contenido propio de 4 es vacío
        out[h] = "\n".join(lineas[i + 1:fin])
    return out, [h for _, h in marcas]


def tabla(bloque):
    """Filas de la primera tabla Markdown del bloque: (encabezado, filas)."""
    filas = []
    for l in bloque.splitlines():
        l = l.strip()
        if l.startswith("|"):
            celdas = [c.strip() for c in l.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c) for c in celdas):
                continue
            filas.append(celdas)
    if not filas:
        return None, []
    return filas[0], filas[1:]


def bullets(bloque):
    return [l.strip() for l in bloque.splitlines() if l.strip().startswith(("- ", "* "))]


def validar(ruta):
    with open(ruta, encoding="utf-8") as f:
        texto = f.read()
    r = []  # (nombre, ok, detalle)

    def chk(nombre, ok, detalle=""):
        r.append((nombre, bool(ok), detalle))

    primera = next((l for l in texto.splitlines() if l.strip()), "")
    chk("Título '# Informe semanal — semana del ...'", primera.startswith("# Informe semanal"), primera[:70])
    chk("Línea 'Contrato: vN'", re.search(r"^Contrato:\s*v\d+", texto, re.M), "")

    sec, orden = secciones(texto)
    chk("Los 7 títulos, en orden y sin secciones extra",
        orden == ENCABEZADOS and len(re.findall(r"^#{2,3} ", texto, re.M)) == len(ENCABEZADOS),
        f"encontrados: {len(orden)}; títulos totales ## / ###: {len(re.findall(r'^#{2,3} ', texto, re.M))}")

    # 1. Control de insumos
    cab, filas = tabla(sec.get(ENCABEZADOS[0], ""))
    chk("1. Columnas exactas", cab == CAB_S1, str(cab))
    chk("1. Cinco filas Lunes..Viernes", [f[0] for f in filas] == DIAS, str([f[0] for f in filas]))
    chk("1. Daily/Cierre solo Sí/No", all(len(f) >= 3 and f[1] in ("Sí", "No") and f[2] in ("Sí", "No") for f in filas), "")
    chk("1. Línea 'Insumos leídos: n/10'", re.search(r"Insumos leídos:\s*\d+/10", sec.get(ENCABEZADOS[0], "")), "")

    # 2. Resumen
    b = bullets(sec.get(ENCABEZADOS[1], ""))
    chk("2. Entre 3 y 5 bullets", 3 <= len(b) <= 5, f"{len(b)} bullets")
    chk("2. Cada bullet con fuente [día-tipo]", all(TAG.search(x) for x in b), f"sin fuente: {sum(1 for x in b if not TAG.search(x))}")
    chk("2. Bullets de hasta 35 palabras", all(len(x[2:].split()) <= 35 for x in b), f"máx: {max((len(x[2:].split()) for x in b), default=0)}")

    # 3. Expectativas
    bl3 = sec.get(ENCABEZADOS[2], "")
    if SIN_EXPECTATIVAS in bl3:
        chk("3. Sin expectativas (frase exacta)", True, "")
    else:
        cab, filas = tabla(bl3)
        chk("3. Columnas exactas", cab == CAB_S3, str(cab))
        chk("3. Hasta 8 filas", 1 <= len(filas) <= 8, f"{len(filas)} filas")
        chk("3. Estado dentro de los 4 permitidos", all(len(f) >= 5 and f[4] in ESTADOS for f in filas), str([f[4] for f in filas if len(f) >= 5 and f[4] not in ESTADOS]))
        chk("3. Cada fila con fuente [día-tipo]", all(TAG.search(" ".join(f)) for f in filas), "")

    # 4.1 Macro
    cab, filas = tabla(sec.get(ENCABEZADOS[4], ""))
    chk("4.1 Columnas exactas", cab == CAB_S41, str(cab))
    chk("4.1 Diez variables fijas, en orden", [f[0] for f in filas] == VARIABLES, str([f[0] for f in filas]))
    chk("4.1 Fuente con [día-tipo] o n/d", all(len(f) >= 6 and (TAG.search(f[5]) or f[5] == "n/d") for f in filas),
        str([f[0] for f in filas if len(f) >= 6 and not (TAG.search(f[5]) or f[5] == "n/d")]))

    # 4.2 Sector
    bl42 = sec.get(ENCABEZADOS[5], "")
    b = bullets(bl42)
    if SIN_SECTOR in bl42:
        chk("4.2 Frase exacta 'sin información sectorial'", not b, "")
    else:
        chk("4.2 Hasta 3 bullets con fuente", 1 <= len(b) <= 3 and all(TAG.search(x) for x in b), f"{len(b)} bullets")

    # 5. Límites
    bl5 = sec.get(ENCABEZADOS[6], "")
    b = bullets(bl5)
    chk("5. Hasta 3 bullets o 'Sin observaciones.'", (SIN_OBS in bl5 and not b) or 1 <= len(b) <= 3, f"{len(b)} bullets")

    # Transversales
    palabras = len(re.findall(r"\S+", texto))
    chk(f"Extensión hasta {MAX_PALABRAS} palabras", palabras <= MAX_PALABRAS, f"{palabras} palabras")
    if os.path.exists(RUTA_PROHIBIDAS):
        with open(RUTA_PROHIBIDAS, encoding="utf-8") as f:
            prohibidas = [l.strip() for l in f if l.strip()]
        halladas = [p for p in prohibidas if re.search(r"\b" + re.escape(p) + r"\b", texto, re.I)]
        chk("No nombra a la entidad que produce los informes", not halladas, f"{len(halladas)} término(s) de la lista local")
    else:
        r.append(("No nombra a la entidad (OMITIDO: falta " + RUTA_PROHIBIDAS + ")", None, ""))
    return r


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    hubo_fallas = False
    for ruta in sys.argv[1:]:
        print(f"\n== {ruta}")
        res = validar(ruta)
        for nombre, ok, detalle in res:
            marca = "----" if ok is None else ("OK  " if ok else "FALLA")
            print(f"  [{marca}] {nombre}" + (f"  -> {detalle}" if (detalle and not ok) else ""))
        aplicados = [ok for _, ok, _ in res if ok is not None]
        n_ok = sum(1 for ok in aplicados if ok)
        print(f"  Resultado: {n_ok}/{len(aplicados)} chequeos OK" + ("" if len(aplicados) == len(res) else " (hay chequeos omitidos)"))
        hubo_fallas |= n_ok != len(aplicados)
    sys.exit(1 if hubo_fallas else 0)
