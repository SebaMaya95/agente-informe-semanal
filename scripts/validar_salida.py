"""Valida que una salida respete el formato definido en system_prompt.md (sección 5).

Uso, desde la raíz del repo:
    python scripts/validar_salida.py [--spec v1|v2] salidas/corrida_1_....md [otra.md ...]

Cada versión del contrato tiene su especificación (--spec, por defecto la vigente, v2):
  v1: las salidas de la corrida 1 (21 chequeos).
  v2: cambia la tabla 4.1 (columnas, nombres de fila, "Tipo de dato") y agrega las reglas de
      redacción para no especialistas (sin jerga) y los límites de longitud de bullets y celdas,
      que ya estaban escritos en v1 pero no se chequeaban (en la corrida 1 se midieron a mano).

Chequea estructura y redacción mecánica, no la calidad del análisis: títulos y orden, columnas
de las tablas, filas, valores permitidos, fuentes en cada afirmación, extensión, jerga y que no
aparezca el nombre de la entidad que produce los informes. Sale con código 1 si algo falla.
La lista de jerga de v2 se definió a partir de la regla de estilo de v2 y de la jerga que se vio
en la corrida 1; es una señal mecánica, no una prueba de que el texto sea claro.
"""
import os
import re
import sys

ENCABEZADOS_BASE = [
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
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
ESTADOS = {"Cumplida", "No cumplida", "Abierta", "Sin evidencia"}
TIPOS_DATO = {"Cierre", "Daily", "Mixto", "n/d"}
SIN_EXPECTATIVAS = "Sin expectativas explícitas en los informes de esta semana."
SIN_SECTOR = "Sin información sectorial en los informes de esta semana."
SIN_OBS = "Sin observaciones."
MAX_PALABRAS = 1200
MAX_BULLET, MAX_CELDA = 35, 25
TAG = re.compile(r"\[(lun|mar|mie|jue|vie)-(daily|cierre)\]")

SPECS = {
    "v1": {
        "h41": "### 4.1 Variables macro",
        "cab41": ["Variable", "Cierre lunes", "Cierre viernes", "Cambio", "Lectura para el agro", "Fuente"],
        "variables": [
            "Dólar mayorista (A3500)", "Dólar CCL", "Brecha CCL", "Dólar MEP", "Tasas en pesos",
            "Riesgo país", "Treasury 10 años", "Petróleo (Brent)",
            "Compras del BCRA y liquidación del agro", "Acción Cresud (CRES)",
        ],
        "idx_fuente": 5,
        "v2": False,
    },
    "v2": {
        "h41": "### 4.1 Variables económicas",
        "cab41": ["Variable", "Inicio de semana", "Fin de semana", "Cambio", "Tipo de dato", "Lectura para el agro", "Fuente"],
        "variables": [
            "Dólar oficial (mayorista)", "Dólar financiero (CCL)", "Brecha entre dólar financiero y oficial",
            "Dólar bolsa (MEP)", "Tasas de interés en pesos", "Riesgo país", "Tasa de EE.UU. a 10 años",
            "Petróleo (Brent)", "Compras del Banco Central y dólares del agro", "Acción de Cresud",
        ],
        "idx_fuente": 6,
        "v2": True,
    },
}

# Jerga que la regla de estilo de v2 pide evitar. Siglas y códigos: se buscan con mayúsculas exactas.
JERGA = ["pbs", "puntos básicos", "TEA", "TNA", "TIR", "BCRA", "LECAP", "Lecap", "REM", "IPC", "YTD",
         "rollover", "Treasury", "Treasuries", "spread", "duration", "intradía", "intradia", "ON", "ONs",
         "Globales", "Bonares", "caución", "MLC", "FX", "TAMAR", "CER", "A3500", "Senebi"]
JERGA_REGEX = [r"\b(?:GD|AL|AE|AO|AN)\d{2}D?\b", r"\bS\d{2}[A-Z]\d\b", r"(?<=\d)\s?M\b"]

# Términos que no pueden aparecer en la salida (el nombre de la entidad que produce los informes).
# La lista no se publica: vive en insumos/terminos_prohibidos.txt, un término por línea.
RUTA_PROHIBIDAS = os.path.join("insumos", "terminos_prohibidos.txt")


def secciones(texto, encabezados):
    """Devuelve {encabezado: contenido} y la lista de encabezados encontrados, en orden."""
    lineas = texto.splitlines()
    marcas = [(i, l.strip()) for i, l in enumerate(lineas) if l.strip() in encabezados]
    out = {}
    for n, (i, h) in enumerate(marcas):
        fin = marcas[n + 1][0] if n + 1 < len(marcas) else len(lineas)
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


def jerga_hallada(texto):
    """Términos de jerga presentes en el texto (sin contar las etiquetas fijas de la tabla 4.1)."""
    limpio = re.sub(r"\[(?:lun|mar|mie|jue|vie)-(?:daily|cierre)\]", "", texto)
    hallados = []
    for t in JERGA:
        n = len(re.findall(r"(?<![\wÀ-ÿ])" + re.escape(t) + r"(?![\wÀ-ÿ])", limpio))
        if n:
            hallados.append(f"{t} x{n}")
    for rx in JERGA_REGEX:
        n = len(re.findall(rx, limpio))
        if n:
            hallados.append(f"/{rx}/ x{n}")
    return hallados


def validar(ruta, spec_name):
    spec = SPECS[spec_name]
    encabezados = list(ENCABEZADOS_BASE)
    encabezados[4] = spec["h41"]
    with open(ruta, encoding="utf-8") as f:
        texto = f.read()
    r = []  # (nombre, ok, detalle)

    def chk(nombre, ok, detalle=""):
        r.append((nombre, bool(ok), detalle))

    primera = next((l for l in texto.splitlines() if l.strip()), "")
    chk("Título '# Informe semanal — semana del ...'", primera.startswith("# Informe semanal"), primera[:70])
    chk("Línea 'Contrato: vN'", re.search(r"^Contrato:\s*v\d+", texto, re.M), "")

    sec, orden = secciones(texto, encabezados)
    total_titulos = len(re.findall(r"^#{2,3} ", texto, re.M))
    chk("Los 7 títulos, en orden y sin secciones extra", orden == encabezados and total_titulos == len(encabezados),
        f"encontrados: {len(orden)}; títulos totales ## / ###: {total_titulos}")

    # 1. Control de insumos
    cab, filas = tabla(sec.get(encabezados[0], ""))
    chk("1. Columnas exactas", cab == CAB_S1, str(cab))
    chk("1. Cinco filas Lunes..Viernes", [f[0] for f in filas] == DIAS, str([f[0] for f in filas]))
    chk("1. Daily/Cierre solo Sí/No", all(len(f) >= 3 and f[1] in ("Sí", "No") and f[2] in ("Sí", "No") for f in filas), "")
    chk("1. Línea 'Insumos leídos: n/10'", re.search(r"Insumos leídos:\s*\d+/10", sec.get(encabezados[0], "")), "")

    # 2. Resumen
    b = bullets(sec.get(encabezados[1], ""))
    chk("2. Entre 3 y 5 bullets", 3 <= len(b) <= 5, f"{len(b)} bullets")
    chk("2. Cada bullet con fuente [día-tipo]", all(TAG.search(x) for x in b), f"sin fuente: {sum(1 for x in b if not TAG.search(x))}")
    chk("2. Bullets de hasta 35 palabras", all(len(x[2:].split()) <= MAX_BULLET for x in b), f"máx: {max((len(x[2:].split()) for x in b), default=0)}")

    # 3. Expectativas
    bl3 = sec.get(encabezados[2], "")
    if SIN_EXPECTATIVAS in bl3:
        chk("3. Sin expectativas (frase exacta)", True, "")
    else:
        cab, filas = tabla(bl3)
        chk("3. Columnas exactas", cab == CAB_S3, str(cab))
        chk("3. Hasta 8 filas", 1 <= len(filas) <= 8, f"{len(filas)} filas")
        chk("3. Estado dentro de los 4 permitidos", all(len(f) >= 5 and f[4] in ESTADOS for f in filas), str([f[4] for f in filas if len(f) >= 5 and f[4] not in ESTADOS]))
        chk("3. Cada fila con fuente [día-tipo]", all(TAG.search(" ".join(f)) for f in filas), "")

    # 4.1 Variables
    cab, filas41 = tabla(sec.get(encabezados[4], ""))
    ifu = spec["idx_fuente"]
    chk("4.1 Columnas exactas", cab == spec["cab41"], str(cab))
    chk("4.1 Diez variables fijas, en orden", [f[0] for f in filas41] == spec["variables"], str([f[0] for f in filas41]))
    chk("4.1 Fuente con [día-tipo] o n/d", all(len(f) > ifu and (TAG.search(f[ifu]) or f[ifu] == "n/d") for f in filas41),
        str([f[0] for f in filas41 if len(f) > ifu and not (TAG.search(f[ifu]) or f[ifu] == "n/d")]))
    if spec["v2"]:
        chk("4.1 Tipo de dato: Cierre, Daily, Mixto o n/d", all(len(f) > 4 and f[4] in TIPOS_DATO for f in filas41),
            str([(f[0], f[4]) for f in filas41 if len(f) > 4 and f[4] not in TIPOS_DATO]))
        chk("4.1 Cambio solo si el tipo de dato es Cierre (si no, n/d)",
            all(len(f) > 4 and (f[4] == "Cierre" or f[3] == "n/d") for f in filas41),
            str([(f[0], f[4], f[3]) for f in filas41 if len(f) > 4 and f[4] != "Cierre" and f[3] != "n/d"]))

    # 4.2 Sector
    bl42 = sec.get(encabezados[5], "")
    b42 = bullets(bl42)
    if SIN_SECTOR in bl42:
        chk("4.2 Frase exacta 'sin información sectorial'", not b42, "")
    else:
        chk("4.2 Hasta 3 bullets con fuente", 1 <= len(b42) <= 3 and all(TAG.search(x) for x in b42), f"{len(b42)} bullets")

    # 5. Límites
    bl5 = sec.get(encabezados[6], "")
    b5 = bullets(bl5)
    chk("5. Hasta 3 bullets o 'Sin observaciones.'", (SIN_OBS in bl5 and not b5) or 1 <= len(b5) <= 3, f"{len(b5)} bullets")

    # Transversales
    palabras = len(re.findall(r"\S+", texto))
    chk(f"Extensión hasta {MAX_PALABRAS} palabras", palabras <= MAX_PALABRAS, f"{palabras} palabras")
    if spec["v2"]:
        todos_b = [x for l in texto.splitlines() for x in [l.strip()] if x.startswith(("- ", "* "))]
        largos = [len(x[2:].split()) for x in todos_b if len(x[2:].split()) > MAX_BULLET]
        chk(f"Todos los bullets de hasta {MAX_BULLET} palabras", not largos, f"excesos: {largos}")
        celdas = [c for l in texto.splitlines() if l.strip().startswith("|") and not re.fullmatch(r"[|\-\s:]+", l.strip())
                  for c in l.strip().strip("|").split("|")]
        largas = [len(c.split()) for c in celdas if len(c.split()) > MAX_CELDA]
        chk(f"Todas las celdas de hasta {MAX_CELDA} palabras", not largas, f"excesos: {largas}")
        # las etiquetas fijas de la tabla 4.1 no cuentan como jerga (incluyen CCL, MEP y Brent a propósito)
        jerga = jerga_hallada(texto)
        chk("Sin jerga del mercado de capitales (regla de estilo)", not jerga, "; ".join(jerga[:12]) + (" ..." if len(jerga) > 12 else ""))

    if os.path.exists(RUTA_PROHIBIDAS):
        with open(RUTA_PROHIBIDAS, encoding="utf-8") as f:
            prohibidas = [l.strip() for l in f if l.strip()]
        halladas = [p for p in prohibidas if re.search(r"\b" + re.escape(p) + r"\b", texto, re.I)]
        chk("No nombra a la entidad que produce los informes", not halladas, f"{len(halladas)} término(s) de la lista local")
    else:
        r.append(("No nombra a la entidad (OMITIDO: falta " + RUTA_PROHIBIDAS + ")", None, ""))
    return r


if __name__ == "__main__":
    args = sys.argv[1:]
    spec_name = "v2"
    if "--spec" in args:
        i = args.index("--spec")
        spec_name = args[i + 1]
        del args[i:i + 2]
    if not args or spec_name not in SPECS:
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8")
    hubo_fallas = False
    for ruta in args:
        print(f"\n== {ruta}  (spec {spec_name})")
        res = validar(ruta, spec_name)
        for nombre, ok, detalle in res:
            marca = "----" if ok is None else ("OK  " if ok else "FALLA")
            print(f"  [{marca}] {nombre}" + (f"  -> {detalle}" if (detalle and not ok) else ""))
        aplicados = [ok for _, ok, _ in res if ok is not None]
        n_ok = sum(1 for ok in aplicados if ok)
        print(f"  Resultado: {n_ok}/{len(aplicados)} chequeos OK" + ("" if len(aplicados) == len(res) else " (hay chequeos omitidos)"))
        hubo_fallas |= n_ok != len(aplicados)
    sys.exit(1 if hubo_fallas else 0)
