"""Arma el agente a partir de system_prompt.md, sin retocarlo.

Uso, desde la raíz del repo:
    python scripts/preparar_agente.py

Genera .claude/agents/analista-semanal.md: un encabezado técnico (nombre, herramientas,
modelo) seguido del contenido exacto de system_prompt.md, que pasa a ser el system prompt
del agente. El user prompt se envía como mensaje al invocarlo.

Herramientas: solo lectura de los insumos y escritura del informe. Sin web ni shell, lo que
refuerza la restricción de "usar solo la información de los archivos de la semana".
"""
import os

MODELO = "sonnet"
HERRAMIENTAS = "Read, Glob, Grep, Write"

with open("system_prompt.md", encoding="utf-8") as f:
    system_prompt = f.read().strip()

encabezado = (
    "---\n"
    "name: analista-semanal\n"
    "description: Analista semanal de mercado con foco agro. Lee los daily y los cierres de una semana y escribe el informe estructurado.\n"
    f"tools: {HERRAMIENTAS}\n"
    f"model: {MODELO}\n"
    "---\n\n"
)

os.makedirs(os.path.join(".claude", "agents"), exist_ok=True)
with open(os.path.join(".claude", "agents", "analista-semanal.md"), "w", encoding="utf-8") as f:
    f.write(encabezado + system_prompt + "\n")

print("Agente escrito en .claude/agents/analista-semanal.md")
