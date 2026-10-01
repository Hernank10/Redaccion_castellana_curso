# -*- coding: utf-8 -*-
"""add_extra_head.py"""
from pathlib import Path

p = Path(r"E:\02_proyectos\Redaccion_castellana_curso-main\templates\core\base.html")
txt = p.read_text(encoding="utf-8")

if "block extra_head" in txt:
    print("extra_head ya existe")
else:
    # Insertar antes del cierre </head>
    if "</head>" in txt:
        txt = txt.replace("</head>", "    {% block extra_head %}{% endblock %}\n</head>", 1)
        p.write_text(txt, encoding="utf-8")
        print("OK: bloque extra_head anadido a base.html")
    else:
        print("ERROR: no se encontro </head>")