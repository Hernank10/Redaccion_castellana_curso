# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""redaccion_i18n.py - Pipeline i18n."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(r"E:\02_proyectos\Redaccion_castellana_curso-main")
PYDJ5 = r"E:\PythonPortable_Django5\python.exe"
SETTINGS = BASE / "lms_vector" / "settings.py"
URLS = BASE / "lms_vector" / "urls.py"
TEMPLATES = BASE / "templates"
JSON_FILE = BASE / "traducciones.json"

IDIOMAS = ["es", "en", "zh_Hans", "hi", "ar", "fr", "pt", "ru", "bn",
           "ur", "ja", "de", "ko", "it", "tr", "vi"]

CADENAS = [
    "Inicio", "Progreso", "Profesor", "Dashboard", "Panel",
    "Archivo de Vector", "Entrar", "Salir", "Registrarse",
    "Lecciones", "Ejercicios", "Curso", "Estudiante", "Admin",
    "Bienvenido", "Continuar", "Volver", "Siguiente", "Anterior",
    "Guardar", "Cancelar", "Enviar", "Buscar",
    "Mis cursos", "Mi progreso", "Mis logros", "Mis certificados",
    "Iniciar sesion", "Crear cuenta", "Cerrar sesion",
    "Usuario", "Contrasena", "Correo electronico",
    "Titulo", "Descripcion", "Nivel", "Puntuacion",
]


def cargar_trad():
    with JSON_FILE.open(encoding="utf-8-sig") as f:
        return json.load(f)


def backup(ruta):
    bak = ruta.with_suffix(ruta.suffix + ".bak")
    if not bak.exists():
        shutil.copy2(ruta, bak)


def asegurar_load_i18n(c):
    if "{% load i18n %}" in c:
        return c
    return "{% load i18n %}\n" + c


def marcar_cadena(c, cad):
    esc = re.escape(cad)
    patron = re.compile(r'(>\s*)(' + esc + r')(\s*<)', re.UNICODE)
    if '{% trans "' + cad + '" %}' in c:
        return c, 0
    return patron.subn(r'\1{% trans "' + cad + r'" %}\3', c)


def fase1():
    print("FASE 1 - Configurar")
    backup(SETTINGS)
    c = SETTINGS.read_text(encoding="utf-8")
    if "LocaleMiddleware" not in c:
        c = c.replace(
            "'django.contrib.sessions.middleware.SessionMiddleware',",
            "'django.contrib.sessions.middleware.SessionMiddleware',\n    'django.middleware.locale.LocaleMiddleware',",
        )
        print("  + LocaleMiddleware")
    if "LANGUAGES = [" not in c:
        b = "\nfrom django.utils.translation import gettext_lazy as _\n\nLANGUAGES = [\n"
        for code in IDIOMAS:
            cs = "zh-hans" if code == "zh_Hans" else code
            b += '    ("' + cs + '", _("' + code + '")),\n'
        b += "]\n\nLOCALE_PATHS = [BASE_DIR / 'locale']\n"
        c += b
        print("  + LANGUAGES + LOCALE_PATHS")
    SETTINGS.write_text(c, encoding="utf-8")
    backup(URLS)
    u = URLS.read_text(encoding="utf-8")
    if "i18n_patterns" not in u:
        u = u.replace(
            "from django.conf.urls.static import static",
            "from django.conf.urls.static import static\nfrom django.conf.urls.i18n import i18n_patterns",
        )
        u = u.replace(
            "urlpatterns = [\n    path('admin/', admin.site.urls),\n    path('', include('core.urls')),\n]",
            "urlpatterns = [\n    path('admin/', admin.site.urls),\n    path('i18n/', include('django.conf.urls.i18n')),\n]\n\nurlpatterns += i18n_patterns(\n    path('', include('core.urls')),\n)",
        )
        print("  + i18n_patterns")
    URLS.write_text(u, encoding="utf-8")


def fase2():
    print("FASE 2 - Marcar cadenas")
    pl = sorted(TEMPLATES.rglob("*.html"))
    print("Plantillas: " + str(len(pl)))
    tg = 0
    for p in pl:
        c = p.read_text(encoding="utf-8")
        t = 0
        for cad in CADENAS:
            c, n = marcar_cadena(c, cad)
            t += n
        if t > 0:
            c = asegurar_load_i18n(c)
            backup(p)
            p.write_text(c, encoding="utf-8")
            print("  OK " + p.name + " -> " + str(t))
            tg += t
    print("TOTAL: " + str(tg))


def fase3():
    print("FASE 3 - makemessages")
    langs = " ".join(["-l " + l for l in IDIOMAS])
    cmd = PYDJ5 + " manage.py makemessages " + langs + " --ignore=venv --ignore=.venv --ignore=env --ignore=static --ignore=media"
    subprocess.run(cmd, shell=True, cwd=str(BASE))


def fase4():
    print("FASE 4 - Rellenar .po")
    trad = cargar_trad()
    LOCALE = BASE / "locale"
    total = 0
    for idioma in IDIOMAS:
        po = LOCALE / idioma / "LC_MESSAGES" / "django.po"
        if not po.exists():
            continue
        contenido = po.read_text(encoding="utf-8")
        lineas = contenido.split("\n")
        salida = []
        i = 0
        cam = 0
        while i < len(lineas):
            ln = lineas[i]
            salida.append(ln)
            if ln.startswith('msgid "') and ln != 'msgid ""':
                mid = ln[7:].rstrip('"')
                if i + 1 < len(lineas) and lineas[i + 1].strip() == 'msgstr ""' and mid:
                    t = trad.get(mid, {}).get(idioma)
                    if t:
                        salida.append('msgstr "' + t + '"')
                        cam += 1
                        i += 2
                        continue
            i += 1
        if cam > 0:
            po.write_text("\n".join(salida), encoding="utf-8")
        print("  " + idioma + " " + str(cam))
        total += cam
    print("TOTAL: " + str(total))


def fase5():
    print("FASE 5 - compilemessages")
    subprocess.run(PYDJ5 + " manage.py compilemessages", shell=True, cwd=str(BASE))


def main():
    print("REDACCION i18n")
    if not BASE.exists():
        return
    f = sys.argv[1:] if len(sys.argv) > 1 else ["1", "2", "3", "4", "5"]
    if "1" in f: fase1()
    if "2" in f: fase2()
    if "3" in f: fase3()
    if "4" in f: fase4()
    if "5" in f: fase5()
    print("LISTO")


if __name__ == "__main__":
    main()
