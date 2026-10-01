# -*- coding: utf-8 -*-
"""integrar_certif.py"""
from pathlib import Path

p = Path(r"E:\02_proyectos\Redaccion_castellana_curso-main\core\views.py")
txt = p.read_text(encoding="utf-8")

if "crear_notificacion_certificado" in txt:
    print("Ya integrado")
else:
    viejo = """    return redirect('teacher_course_students', curso_slug=curso.slug)


@staff_member_required
def teacher_student_progress_pdf"""
    nuevo = """    if created:
        crear_notificacion_certificado(estudiante, curso)

    return redirect('teacher_course_students', curso_slug=curso.slug)


@staff_member_required
def teacher_student_progress_pdf"""
    if viejo in txt:
        txt = txt.replace(viejo, nuevo, 1)
        p.write_text(txt, encoding="utf-8")
        print("OK: integracion de certificado")
    else:
        print("No encontrado. Anade manualmente tras Certificado.objects.get_or_create")