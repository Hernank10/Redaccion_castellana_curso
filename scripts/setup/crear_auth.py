# -*- coding: utf-8 -*-
"""crear_auth.py - Login/registro/logout + dashboards."""
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
    print("FASE 1 - URLs auth")
    backup(URLS)
    c = URLS.read_text(encoding="utf-8")
    if "registro" in c:
        print("  ya existe")
        return
    if "from django.contrib.auth import views as auth_views" not in c:
        c = "from django.contrib.auth import views as auth_views\n" + c
    c = c.replace(
        "    path('', views.index, name='index'),",
        "    path('', views.index, name='index'),\n    path('registro/', views.registro, name='registro'),\n    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),\n    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),"
    )
    URLS.write_text(c, encoding="utf-8")
    print("  + URLs registro/login/logout")


def fase2_vista_registro():
    print("FASE 2 - Vista registro")
    backup(VIEWS)
    c = VIEWS.read_text(encoding="utf-8")
    if "def registro" in c:
        print("  ya existe")
        return
    codigo = """

def registro(request):
    from django.contrib import messages
    from django.contrib.auth.models import User
    from django.shortcuts import redirect
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.error(request, 'Usuario y contrasena son obligatorios')
            return render(request, 'core/registro.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
            return render(request, 'core/registro.html')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Cuenta creada. Ahora puedes iniciar sesion.')
        return redirect('login')
    return render(request, 'core/registro.html')
"""
    c += codigo
    VIEWS.write_text(c, encoding="utf-8")
    print("  + Vista registro")
def fase3_login_html():
    print("FASE 3 - login.html")
    html = """{% extends 'core/base.html' %}
{% load i18n %}
{% block title %}{% trans "Iniciar sesion" %}{% endblock %}
{% block content %}
<div style="max-width:400px;margin:80px auto;padding:30px;background:#1a1a2e;border:1px solid #333;border-radius:12px;">
    <h1 style="text-align:center;color:#00d4ff;font-family:Orbitron,sans-serif;">
        <i class="fas fa-sign-in-alt"></i> {% trans "Iniciar sesion" %}
    </h1>
    <form method="post" style="margin-top:30px;">
        {% csrf_token %}
        <div style="margin-bottom:15px;">
            <label style="color:#ccc;display:block;margin-bottom:5px;">{% trans "Usuario" %}</label>
            <input type="text" name="username" required style="width:100%;padding:10px;background:#0f0f1e;border:1px solid #444;border-radius:6px;color:#fff;">
        </div>
        <div style="margin-bottom:20px;">
            <label style="color:#ccc;display:block;margin-bottom:5px;">{% trans "Contrasena" %}</label>
            <input type="password" name="password" required style="width:100%;padding:10px;background:#0f0f1e;border:1px solid #444;border-radius:6px;color:#fff;">
        </div>
        <button type="submit" style="width:100%;padding:12px;background:#00d4ff;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:1rem;">
            {% trans "Entrar" %}
        </button>
    </form>
    <p style="text-align:center;color:#aaa;margin-top:20px;">
        {% trans "No tienes cuenta?" %} <a href="{% url 'registro' %}" style="color:#00d4ff;">{% trans "Registrate" %}</a>
    </p>
</div>
{% endblock %}
"""
    (TEMPLATES / "login.html").write_text(html, encoding="utf-8")
    print("  + login.html")
def fase4_registro_html():
    print("FASE 4 - registro.html")
    html = """{% extends 'core/base.html' %}
{% load i18n %}
{% block title %}{% trans "Registro" %}{% endblock %}
{% block content %}
<div style="max-width:400px;margin:80px auto;padding:30px;background:#1a1a2e;border:1px solid #333;border-radius:12px;">
    <h1 style="text-align:center;color:#00d4ff;font-family:Orbitron,sans-serif;">
        <i class="fas fa-user-plus"></i> {% trans "Crear cuenta" %}
    </h1>
    {% if messages %}
        {% for message in messages %}
            <div style="padding:10px;margin:15px 0;border-radius:6px;background:{% if message.tags == 'error' %}#4a1a1a{% else %}#1a4a1a{% endif %};color:#fff;">
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}
    <form method="post" style="margin-top:20px;">
        {% csrf_token %}
        <div style="margin-bottom:15px;">
            <label style="color:#ccc;display:block;margin-bottom:5px;">{% trans "Usuario" %}</label>
            <input type="text" name="username" required style="width:100%;padding:10px;background:#0f0f1e;border:1px solid #444;border-radius:6px;color:#fff;">
        </div>
        <div style="margin-bottom:15px;">
            <label style="color:#ccc;display:block;margin-bottom:5px;">{% trans "Correo electronico" %}</label>
            <input type="email" name="email" style="width:100%;padding:10px;background:#0f0f1e;border:1px solid #444;border-radius:6px;color:#fff;">
        </div>
        <div style="margin-bottom:20px;">
            <label style="color:#ccc;display:block;margin-bottom:5px;">{% trans "Contrasena" %}</label>
            <input type="password" name="password" required style="width:100%;padding:10px;background:#0f0f1e;border:1px solid #444;border-radius:6px;color:#fff;">
        </div>
        <button type="submit" style="width:100%;padding:12px;background:#00d4ff;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:1rem;">
            {% trans "Crear cuenta" %}
        </button>
    </form>
    <p style="text-align:center;color:#aaa;margin-top:20px;">
        {% trans "Ya tienes cuenta?" %} <a href="{% url 'login' %}" style="color:#00d4ff;">{% trans "Inicia sesion" %}</a>
    </p>
</div>
{% endblock %}
"""
    (TEMPLATES / "registro.html").write_text(html, encoding="utf-8")
    print("  + registro.html")
def fase5_base_html():
    print("FASE 5 - base.html navbar")
    base = TEMPLATES / "base.html"
    backup(base)
    c = base.read_text(encoding="utf-8")
    if "{% url 'registro' %}" in c:
        print("  ya existe")
        return
    viejo = """{% if user.is_authenticated %}
                    <a href="{% url 'dashboard' %}"><i class="fas fa-chart-simple"></i> {% trans "Progreso" %}</a>
                    {% if user.is_staff %}
                        <a href="{% url 'teacher_dashboard' %}"><i class="fas fa-chalkboard-teacher"></i> {% trans "Profesor" %}</a>
                    {% endif %}
                    <span class="nav-user"><i class="fas fa-user"></i> {{ user.username }}</span>
                    <a href="{% url 'admin:logout' %}" class="nav-logout" title="{% trans 'Salir' %}"><i class="fas fa-sign-out-alt"></i></a>
                {% else %}
                    <a href="{% url 'admin:login' %}"><i class="fas fa-sign-in-alt"></i> {% trans "Iniciar sesion" %}</a>
                {% endif %}"""
    nuevo = """{% if user.is_authenticated %}
                    <a href="{% url 'dashboard' %}"><i class="fas fa-chart-simple"></i> {% trans "Mi progreso" %}</a>
                    {% if user.is_staff %}
                        <a href="{% url 'teacher_dashboard' %}"><i class="fas fa-chalkboard-teacher"></i> {% trans "Profesor" %}</a>
                    {% endif %}
                    <span class="nav-user"><i class="fas fa-user"></i> {{ user.username }}</span>
                    <a href="{% url 'logout' %}" class="nav-logout" title="{% trans 'Salir' %}"><i class="fas fa-sign-out-alt"></i></a>
                {% else %}
                    <a href="{% url 'login' %}"><i class="fas fa-sign-in-alt"></i> {% trans "Iniciar sesion" %}</a>
                    <a href="{% url 'registro' %}"><i class="fas fa-user-plus"></i> {% trans "Registro" %}</a>
                {% endif %}"""
    c = c.replace(viejo, nuevo)
    base.write_text(c, encoding="utf-8")
    print("  + base.html actualizado")


def main():
    print("CREAR AUTH")
    if not BASE.exists():
        return
    fase1_urls()
    fase2_vista_registro()
    fase3_login_html()
    fase4_registro_html()
    fase5_base_html()
    print("LISTO")


if __name__ == "__main__":
    main()
