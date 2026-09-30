# -*- coding: utf-8 -*-
"""crear_cursos.py - Cursos/Recursos."""
import shutil
from pathlib import Path

BASE = Path(r"E:\02_proyectos\Redaccion_castellana_curso-main")
VIEWS = BASE / "core" / "views.py"
URLS = BASE / "core" / "urls.py"
TEMPLATES = BASE / "templates" / "core"


def backup(ruta):
    bak = ruta.with_suffix(ruta.suffix + ".bak")
    if not bak.exists():
        shutil.copy2(ruta, bak)


def fase1_urls():
    print("FASE 1 - URLs")
    backup(URLS)
    c = URLS.read_text(encoding="utf-8")
    if "course_list" in c:
        print("  ya existe")
        return
    c = c.replace(
        "    path('', views.index, name='index'),",
        "    path('', views.index, name='index'),\n    path('cursos/', views.course_list, name='course_list'),\n    path('recursos/', views.resource_list, name='resource_list'),"
    )
    URLS.write_text(c, encoding="utf-8")
    print("  + URLs")


def fase2_vistas():
    print("FASE 2 - Vistas")
    backup(VIEWS)
    c = VIEWS.read_text(encoding="utf-8")
    if "def course_list" in c:
        print("  ya existe")
        return
    codigo = """

def course_list(request):
    from .models import Course
    cursos = Course.objects.filter(is_active=True).order_by('order')
    return render(request, 'core/course_list.html', {'cursos': cursos})


def resource_list(request):
    from .models import Lesson
    recursos = Lesson.objects.filter(is_active=True).select_related('course').order_by('course__order', 'order')
    return render(request, 'core/resource_list.html', {'recursos': recursos})
"""
    c += codigo
    VIEWS.write_text(c, encoding="utf-8")
    print("  + Vistas")
def fase3_course_list():
    print("FASE 3 - course_list.html")
    html = """{% extends 'core/base.html' %}
{% load i18n %}
{% block title %}{% trans "Cursos" %} · {% trans "El Archivo de Vector" %}{% endblock %}
{% block content %}
<div style="max-width:1200px;margin:40px auto;padding:0 20px;">
    <h1 style="text-align:center;font-family:Orbitron,sans-serif;color:#00d4ff;">
        <i class="fas fa-book"></i> {% trans "Cursos" %}
    </h1>
    <p style="text-align:center;color:#aaa;margin-bottom:40px;">
        {% trans "Explora los cursos disponibles" %}
    </p>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;">
        {% for curso in cursos %}
        <div style="background:#1a1a2e;border:1px solid #333;border-radius:12px;padding:20px;">
            <div style="font-size:2.5rem;text-align:center;">{{ curso.icon }}</div>
            <h3 style="color:#00d4ff;text-align:center;">{{ curso.name }}</h3>
            <p style="color:#ccc;font-size:0.9rem;text-align:center;">{{ curso.description|truncatechars:80 }}</p>
            <p style="color:#888;font-size:0.8rem;text-align:center;">
                {{ curso.lessons.count }} {% trans "lecciones" %}
            </p>
            <a href="{% url 'course_detail' curso.slug %}" style="display:block;text-align:center;margin-top:15px;background:#00d4ff;color:#000;padding:8px;border-radius:6px;text-decoration:none;font-weight:bold;">
                {% trans "Inscribirse" %}
            </a>
        </div>
        {% empty %}
        <p style="color:#aaa;text-align:center;grid-column:1/-1;">{% trans "No hay cursos disponibles" %}</p>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""
    (TEMPLATES / "course_list.html").write_text(html, encoding="utf-8")
    print("  + course_list.html")
def fase4_course_detail():
    print("FASE 4 - course_detail.html")
    html = """{% extends 'core/base.html' %}
{% load i18n %}
{% block title %}{{ curso.name }} · {% trans "El Archivo de Vector" %}{% endblock %}
{% block content %}
<div style="max-width:1000px;margin:40px auto;padding:0 20px;">
    <a href="{% url 'course_list' %}" style="color:#00d4ff;text-decoration:none;">
        <i class="fas fa-arrow-left"></i> {% trans "Volver a Cursos" %}
    </a>
    <div style="background:#1a1a2e;border:1px solid #333;border-radius:12px;padding:30px;margin-top:20px;">
        <div style="font-size:3rem;text-align:center;">{{ curso.icon }}</div>
        <h1 style="text-align:center;color:#00d4ff;font-family:Orbitron,sans-serif;">{{ curso.name }}</h1>
        <p style="text-align:center;color:#ccc;">{{ curso.description }}</p>
        <p style="text-align:center;color:#888;">
            {{ lecciones.count }} {% trans "lecciones" %}
        </p>
        <a href="#" style="display:block;text-align:center;margin:20px auto;background:#00d4ff;color:#000;padding:12px 30px;border-radius:6px;text-decoration:none;font-weight:bold;max-width:200px;">
            {% trans "Inscribirse al curso" %}
        </a>
    </div>
    <h2 style="color:#fff;margin-top:40px;">{% trans "Lecciones" %}</h2>
    <div style="display:grid;gap:10px;margin-top:20px;">
        {% for leccion in lecciones %}
        <div style="background:#1a1a2e;border:1px solid #333;border-radius:8px;padding:15px;display:flex;justify-content:space-between;align-items:center;">
            <div>
                <strong style="color:#00d4ff;">{{ leccion.order }}. {{ leccion.title }}</strong>
                <p style="color:#aaa;font-size:0.85rem;margin:5px 0 0 0;">{{ leccion.meaning|truncatechars:80 }}</p>
            </div>
            <a href="{% url 'practice_lesson' leccion.id %}" style="background:#00d4ff;color:#000;padding:6px 15px;border-radius:6px;text-decoration:none;white-space:nowrap;">
                {% trans "Practicar" %}
            </a>
        </div>
        {% empty %}
        <p style="color:#aaa;">{% trans "No hay lecciones disponibles" %}</p>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""
    (TEMPLATES / "course_detail.html").write_text(html, encoding="utf-8")
    print("  + course_detail.html")
def fase5_resource_list():
    print("FASE 5 - resource_list.html")
    html = """{% extends 'core/base.html' %}
{% load i18n %}
{% block title %}{% trans "Recursos" %} · {% trans "El Archivo de Vector" %}{% endblock %}
{% block content %}
<div style="max-width:1200px;margin:40px auto;padding:0 20px;">
    <h1 style="text-align:center;font-family:Orbitron,sans-serif;color:#00d4ff;">
        <i class="fas fa-folder-open"></i> {% trans "Recursos" %}
    </h1>
    <p style="text-align:center;color:#aaa;margin-bottom:40px;">
        {% trans "Todos los recursos disponibles" %}
    </p>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:15px;">
        {% for rec in recursos %}
        <div style="background:#1a1a2e;border:1px solid #333;border-radius:8px;padding:15px;">
            <span style="color:#888;font-size:0.8rem;">{{ rec.course.name }}</span>
            <h4 style="color:#00d4ff;margin:5px 0;">{{ rec.title }}</h4>
            <p style="color:#ccc;font-size:0.85rem;">{{ rec.meaning|truncatechars:100 }}</p>
            <a href="{% url 'practice_lesson' rec.id %}" style="color:#00d4ff;text-decoration:none;font-size:0.9rem;">
                {% trans "Practicar" %} <i class="fas fa-arrow-right"></i>
            </a>
        </div>
        {% empty %}
        <p style="color:#aaa;grid-column:1/-1;text-align:center;">{% trans "No hay recursos disponibles" %}</p>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""
    (TEMPLATES / "resource_list.html").write_text(html, encoding="utf-8")
    print("  + resource_list.html")


def main():
    print("CREAR CURSOS/RECURSOS")
    if not BASE.exists():
        return
    fase1_urls()
    fase2_vistas()
    fase3_course_list()
    fase4_course_detail()
    fase5_resource_list()
    print("LISTO")


if __name__ == "__main__":
    main()
