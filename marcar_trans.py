# -*- coding: utf-8 -*-
"""
marcar_trans.py - Marca cadenas visibles con {% trans %} en plantillas.
"""
import re
import shutil
from pathlib import Path

BASE = Path(r"E:\02_proyectos\eduplatform\_original")
TEMPLATES = BASE / "templates"

# Cadenas a marcar (editables por plantilla)
CADENAS = [
    "EduPlatform", "Cursos", "Recursos", "Ejercicios", "Usuarios",
    "Entrar", "Registrarse", "Salir", "Perfil", "Dashboard",
    "Aprende Castellano con 1066 Ejercicios Interactivos",
    "50 cursos, 497 recursos, 8 logros y certificados",
    "Buscar cursos...", "Cursos destacados",
    "Iniciar sesión", "Crear cuenta", "Usuario", "Contraseña",
    "Correo electrónico", "Nombre completo",
    "¿Ya tienes cuenta?", "¿No tienes cuenta?",
    "Lecciones", "Progreso", "Certificados", "Logros",
    "Insignias", "Ranking", "Clasificación",
    "Panel del Estudiante", "Panel del Profesor",
    "Mis cursos", "Mis logros", "Mis certificados",
    "Guardar", "Cancelar", "Continuar", "Volver",
    "Siguiente", "Anterior", "Buscar",
]


def asegurar_load_i18n(contenido):
    if "{% load i18n %}" in contenido:
        return contenido
    if contenido.lstrip().startswith("{% extends"):
        lineas = contenido.split("\n", 1)
        return lineas[0] + "\n{% load i18n %}\n" + (lineas[1] if len(lineas) > 1 else "")
    return "{% load i18n %}\n" + contenido


def marcar_cadena(contenido, cadena):
    """Envuelve la cadena con {% trans %} si aparece como texto visible."""
    cadena_esc = re.escape(cadena)
    # Patrón: >opcional_espacios CADENA espacios<
    patron = re.compile(
        r'(>\s*)(' + cadena_esc + r')(\s*<)',
        re.UNICODE,
    )
    if '{% trans "' + cadena + '" %}' in contenido:
        return contenido, 0
    nuevo, n = patron.subn(r'\1{% trans "' + cadena + r'" %}\3', contenido)
    return nuevo, n


def marcar_plantilla(ruta):
    contenido = ruta.read_text(encoding="utf-8")
    original = contenido
    total = 0
    detalle = {}

    for cadena in CADENAS:
        contenido, n = marcar_cadena(contenido, cadena)
        if n > 0:
            detalle[cadena] = n
            total += n

    if total > 0:
        contenido = asegurar_load_i18n(contenido)
        backup = ruta.with_suffix(ruta.suffix + ".bak")
        if not backup.exists():
            shutil.copy2(ruta, backup)
        ruta.write_text(contenido, encoding="utf-8")

    return total, detalle


def main():
    print("=" * 60)
    print("Marcar cadenas con {% trans %}")
    print("=" * 60)

    plantillas = sorted(TEMPLATES.rglob("*.html"))
    print(f"Plantillas: {len(plantillas)}")
    print()

    total_global = 0
    for p in plantillas:
        total, detalle = marcar_plantilla(p)
        if total > 0:
            print(f"OK {p.relative_to(TEMPLATES)} -> {total}")
            total_global += total

    print()
    print(f"TOTAL: {total_global} cadenas marcadas")


if __name__ == "__main__":
    main()