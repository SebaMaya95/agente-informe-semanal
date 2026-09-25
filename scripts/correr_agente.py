"""Corre el agente sobre una semana, pasando el system prompt como system prompt real.

Uso, desde la raíz del repo:
    python scripts/correr_agente.py --lunes 2026-09-07 --version v2 --archivo corrida_1_semana_2026-09-07.md

Qué hace:
  1. Lee system_prompt.md (o el que indiques con --sistema) y lo pasa tal cual como
     --system-prompt del CLI de Claude Code.
  2. Completa la plantilla user_prompt.md (o --usuario) con la semana, la versión y el
     archivo de destino, y la pasa como mensaje del usuario.
  3. Le da al agente solo cuatro herramientas: Read, Glob, Grep y Write (sin shell ni web).
  4. Desde la corrida 2 el agente corre AISLADO: en una carpeta temporal que contiene solo los
     .txt de la semana y una carpeta salidas/ vacía, con las herramientas de archivos confinadas
     a esa carpeta (--restricted). Así no puede leer el README, los scripts, otras semanas ni
     los contratos anteriores. La corrida 1 no estaba aislada y el agente leyó el README.
  5. El agente escribe el informe; este script solo lo copia a --salida-dir (por defecto
     salidas/) sin tocarlo, y guarda <archivo>.meta.json con qué versión del contrato se usó
     (hash), qué modelo respondió y qué archivos abrió realmente el agente.

Se usa Python y no PowerShell porque PowerShell 5.1 rompe las comillas dobles de un texto
largo al pasarlo como argumento a un programa externo.

Requiere el CLI de Claude Code con sesión iniciada (claude auth login). Si no lo encuentra,
indicá la ruta con --claude o con la variable CLAUDE_EXE.
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

HERRAMIENTAS = "Read,Glob,Grep,Write"


def buscar_claude(indicado):
    if indicado:
        return indicado
    if os.environ.get("CLAUDE_EXE"):
        return os.environ["CLAUDE_EXE"]
    patron = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Packages", "Claude_*", "LocalCache",
                          "Roaming", "Claude", "claude-code", "*", "claude.exe")
    candidatos = sorted(glob.glob(patron))
    if candidatos:
        return candidatos[-1]
    return shutil.which("claude")


def sha(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lunes", required=True, help="fecha del lunes de la semana, AAAA-MM-DD")
    ap.add_argument("--version", required=True, help="etiqueta del contrato, por ejemplo v2")
    ap.add_argument("--archivo", required=True, help="nombre del archivo de salida")
    ap.add_argument("--salida-dir", default="salidas", help="carpeta del repo donde se copia el informe")
    ap.add_argument("--sistema", default="system_prompt.md")
    ap.add_argument("--usuario", default="user_prompt.md")
    ap.add_argument("--modelo", default="sonnet")
    ap.add_argument("--claude", default=None)
    ap.add_argument("--log", default=None, help="donde guardar el log completo de eventos (no se publica)")
    ap.add_argument("--sin-aislar", action="store_true", help="corre dentro del repo, sin carpeta temporal (como la corrida 1)")
    args = ap.parse_args()

    claude = buscar_claude(args.claude)
    if not claude or not os.path.exists(claude):
        sys.exit("No encuentro claude.exe. Indicá la ruta con --claude o CLAUDE_EXE.")

    lunes = dt.date.fromisoformat(args.lunes)
    viernes = lunes + dt.timedelta(days=4)
    carpeta = os.path.join("insumos", f"semana_{lunes.isoformat()}")
    if not os.path.isdir(carpeta):
        sys.exit(f"No existe {carpeta}")

    with open(args.sistema, encoding="utf-8") as f:
        sistema = f.read()
    with open(args.usuario, encoding="utf-8") as f:
        usuario = f.read()
    for k, v in {"{{LUNES}}": lunes.isoformat(), "{{VIERNES}}": viernes.isoformat(),
                 "{{VERSION}}": args.version, "{{ARCHIVO}}": args.archivo}.items():
        usuario = usuario.replace(k, v)
    if "{{" in usuario:
        sys.exit("Quedaron valores sin completar en el user prompt.")

    destino = os.path.join(args.salida_dir, args.archivo)
    if os.path.exists(destino):
        sys.exit(f"Ya existe {destino}: no lo piso. Usá otro nombre o borralo a propósito.")
    os.makedirs(args.salida_dir, exist_ok=True)

    # Entorno de trabajo del agente
    aislado = not args.sin_aislar
    if aislado:
        cwd = tempfile.mkdtemp(prefix="agente_")
        os.makedirs(os.path.join(cwd, carpeta))
        for txt in glob.glob(os.path.join(carpeta, "*.txt")):
            shutil.copy2(txt, os.path.join(cwd, carpeta))
        os.makedirs(os.path.join(cwd, "salidas"))
        escrito = os.path.join(cwd, "salidas", args.archivo)   # el user prompt dice salidas/<archivo>
    else:
        cwd = os.getcwd()
        os.makedirs("salidas", exist_ok=True)
        escrito = os.path.join("salidas", args.archivo)
        destino = escrito

    flags = ["--model", args.modelo, "--tools", HERRAMIENTAS, "--permission-mode", "acceptEdits",
             "--permission-prompts", "none", "--output-format", "stream-json", "--verbose",
             "--no-session-persistence"] + (["--restricted"] if aislado else [])
    cmd = [claude, "-p", usuario, "--system-prompt", sistema] + flags

    inicio = dt.datetime.now()
    print(f"[{inicio:%H:%M:%S}] Corriendo {args.version} sobre la semana {lunes} "
          f"({'aislado' if aislado else 'SIN aislar'}) ... puede tardar varios minutos")
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600, cwd=cwd)
    if args.log:
        os.makedirs(os.path.dirname(os.path.abspath(args.log)), exist_ok=True)
        with open(args.log, "w", encoding="utf-8") as f:
            f.write(p.stdout)

    leidos, resultado, init = [], {}, {}
    for linea in p.stdout.splitlines():
        try:
            ev = json.loads(linea)
        except json.JSONDecodeError:
            continue
        tipo = ev.get("type")
        if tipo == "system" and ev.get("subtype") == "init":
            init = ev
        elif tipo == "assistant":
            for bloque in ev.get("message", {}).get("content", []):
                if bloque.get("type") == "tool_use" and bloque.get("name") == "Read":
                    inp = bloque.get("input", {})
                    leidos.append(inp.get("file_path") or inp.get("path"))
        elif tipo == "result":
            resultado = ev

    def relativa(r):
        try:
            return os.path.relpath(r, cwd).replace("\\", "/")
        except (ValueError, TypeError):
            return str(r)

    distintos = sorted({relativa(r) for r in leidos if r})
    esperados = sorted(f"{carpeta}/{d}_{t}.txt".replace("\\", "/") for d in ("lun", "mar", "mie", "jue", "vie") for t in ("daily", "cierre"))
    salida_ok = os.path.exists(escrito)
    if aislado and salida_ok:
        shutil.copy2(escrito, destino)

    meta = {
        "fecha_hora": inicio.isoformat(timespec="seconds"),
        "semana_lunes": lunes.isoformat(),
        "contrato": args.version,
        "system_prompt_sha256_16": sha(sistema),
        "user_prompt_sha256_16": sha(usuario),
        "modelo_solicitado": args.modelo,
        "modelo_resuelto": init.get("model"),
        "herramientas": HERRAMIENTAS.split(","),
        "entorno_aislado": aislado,
        "banderas_del_cli": list(flags),
        "archivo_salida": destino.replace("\\", "/"),
        "salida_escrita_por_el_agente": salida_ok,
        "archivos_leidos_distintos": distintos,
        "fuera_de_la_semana": [d for d in distintos if not d.startswith(carpeta.replace("\\", "/"))],
        "insumos_esperados_no_leidos": [e for e in esperados if e not in distintos],
        "llamadas_a_read": len(leidos),
        "turnos": resultado.get("num_turns"),
        "duracion_s": round((resultado.get("duration_ms") or 0) / 1000),
        "tokens": {k: resultado.get("usage", {}).get(k) for k in
                   ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")},
        "respuesta_final_del_agente": resultado.get("result"),
        "codigo_de_salida_cli": p.returncode,
    }
    with open(destino + ".meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(json.dumps({k: meta[k] for k in ("modelo_resuelto", "entorno_aislado", "salida_escrita_por_el_agente",
                                            "llamadas_a_read", "fuera_de_la_semana", "turnos", "duracion_s", "tokens",
                                            "insumos_esperados_no_leidos", "respuesta_final_del_agente",
                                            "codigo_de_salida_cli")}, ensure_ascii=False, indent=2))
    if p.returncode != 0 or resultado.get("is_error") or not salida_ok:
        print("\nERROR. stderr del CLI:\n" + p.stderr[-1500:])
        print(f"(se conserva la carpeta de trabajo: {cwd})" if aislado else "")
        sys.exit(1)
    if aislado:
        shutil.rmtree(cwd, ignore_errors=True)


if __name__ == "__main__":
    main()
