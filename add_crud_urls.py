# -*- coding: utf-8 -*-
"""add_crud_urls.py"""
from pathlib import Path
import re

p = Path(r"E:\02_proyectos\Redaccion_castellana_curso-main\core\urls.py")
txt = p.read_text(encoding="utf-8")

if "teacher_course_edit" in txt:
    print("URLs CRUD ya existen")
else:
    patron = re.compile(
        r"(\s*path\('profesor/curso/<slug:curso_slug>/',\s*views\.teacher_course_students,\s*name='teacher_course_students'\),)"
    )
    m = patron.search(txt)
    if m:
        base = m.group(1)
        nuevas = base + """
    path('profesor/curso/nuevo/', views.teacher_course_edit, name='teacher_course_new'),
    path('profesor/curso/<slug:curso_slug>/editar/', views.teacher_course_edit, name='teacher_course_edit'),
    path('profesor/curso/<slug:curso_slug>/borrar/', views.teacher_course_delete, name='teacher_course_delete'),
    path('profesor/curso/<slug:curso_slug>/lecciones/', views.teacher_course_lessons, name='teacher_course_lessons'),
    path('profesor/curso/<slug:curso_slug>/leccion/nueva/', views.teacher_lesson_edit, name='teacher_lesson_new'),
    path('profesor/curso/<slug:curso_slug>/leccion/<int:lesson_id>/editar/', views.teacher_lesson_edit, name='teacher_lesson_edit'),
    path('profesor/curso/<slug:curso_slug>/leccion/<int:lesson_id>/borrar/', views.teacher_lesson_delete, name='teacher_lesson_delete'),"""
        txt = txt.replace(base, nuevas)
        p.write_text(txt, encoding="utf-8")
        print("OK: URLs CRUD anadidas")
    else:
        print("ERROR: no se encontro la linea base")