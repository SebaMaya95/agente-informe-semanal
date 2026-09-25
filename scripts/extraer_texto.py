"""Paso 0 (manual, fuera del contrato): convierte los PDF de insumos/semana_*/ a .txt.

Uso, desde la raíz del repo:
    python scripts/extraer_texto.py [carpeta_insumos]

Requiere: pip install pypdf
Cada PDF genera un .txt al lado, con marcas "=== PAGINA n ===".
"""
import glob
import os
import sys

from pypdf import PdfReader

base = sys.argv[1] if len(sys.argv) > 1 else "insumos"

for pdf in sorted(glob.glob(os.path.join(base, "semana_*", "*.pdf"))):
    lector = PdfReader(pdf)
    partes = [f"=== PAGINA {i} ===\n{(p.extract_text() or '').strip()}" for i, p in enumerate(lector.pages, 1)]
    with open(pdf[:-4] + ".txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(partes) + "\n")
    print(f"{pdf}: {len(lector.pages)} págs")
