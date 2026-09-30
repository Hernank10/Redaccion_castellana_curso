# -*- coding: utf-8 -*-
"""limpiar_marcas.py - Quita marcas de merge dejando la version local (arriba)."""
from pathlib import Path

BASE = Path(r"E:\02_proyectos\Redaccion_castellana_curso-main")
EXT = {".py", ".html", ".json", ".txt", ".md", ".css", ".js", ".po", ".cfg", ".ini"}
IGNORAR = {".git", "__pycache__", "node_modules", ".venv", "venv"}

def resolver(texto):
    salida, en_conf, en_ours = [], False, False
    for linea in texto.splitlines(keepends=True):
        if linea.startswith("<<<<<<<"):
            en_conf, en_ours = True, True
            continue
        if linea.startswith("=======") and en_conf:
            en_ours = False
            continue
        if linea.startswith(">>>>>>>") and en_conf:
            en_conf = False
            continue
        if not en_conf or en_ours:
            salida.append(linea)
    return "".join(salida)

def main():
    print("LIMPIAR MARCAS DE MERGE")
    print("-" * 50)
    total = 0
    for p in BASE.rglob("*"):
        if not p.is_file():
            continue
        if any(parte in IGNORAR for parte in p.parts):
            continue
        if p.suffix.lower() not in EXT:
            continue
        try:
            t = p.read_text(encoding="utf-8-sig", errors="ignore")
        except Exception:
            continue
        if "<<<<<<<" in t and "=======" in t and ">>>>>>>" in t:
            nuevo = resolver(t)
            p.write_text(nuevo, encoding="utf-8")
            print("Limpiado: " + str(p.relative_to(BASE)))
            total += 1
    print("-" * 50)
    print("Archivos limpiados: " + str(total))
    if total == 0:
        print("No habia marcas de merge.")

if __name__ == "__main__":
    main()