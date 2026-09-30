# -*- coding: utf-8 -*-
"""patch_json.py - Inserta Cursos y Recursos en actualizar_json.py"""
from pathlib import Path

BASE = Path(r"E:\02_proyectos\Redaccion_castellana_curso-main")
SCRIPT = BASE / "actualizar_json.py"

texto = SCRIPT.read_text(encoding="utf-8-sig")

if '"Cursos"' in texto and '"Recursos"' in texto:
    print("Ya estan las claves. Nada que hacer.")
    raise SystemExit

nuevas = '''    "Cursos": {
        "es": "Cursos", "en": "Courses",
        "zh_Hans": "课程", "hi": "पाठ्यक्रम",
        "ar": "الدورات", "fr": "Cours",
        "pt": "Cursos", "ru": "Курсы",
        "bn": "কোর্স", "ur": "کورسز",
        "ja": "コース", "de": "Kurse",
        "ko": "코스", "it": "Corsi",
        "tr": "Kurslar", "vi": "Khóa học"
    },
    "Recursos": {
        "es": "Recursos", "en": "Resources",
        "zh_Hans": "资源", "hi": "संसाधन",
        "ar": "الموارد", "fr": "Ressources",
        "pt": "Recursos", "ru": "Ресурсы",
        "bn": "সম্পদ", "ur": "وسائل",
        "ja": "リソース", "de": "Ressourcen",
        "ko": "리소스", "it": "Risorse",
        "tr": "Kaynaklar", "vi": "Tài nguyên"
    },
'''

marca = "NUEVAS = {"
idx = texto.find(marca)
if idx == -1:
    print("ERROR: no se encontro 'NUEVAS = {'")
    raise SystemExit

insertar_en = idx + len(marca)
nuevo_texto = texto[:insertar_en] + "\n" + nuevas + texto[insertar_en:]

SCRIPT.write_text(nuevo_texto, encoding="utf-8")
print("OK: Cursos y Recursos insertados en actualizar_json.py")
