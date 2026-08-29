# ⌛ Archivo de Vector

**LMS Educativa · 100+ técnicas de redacción en castellano**

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-4.2.7-green)
![SQLite](https://img.shields.io/badge/SQLite-3-cyan)
![MySQL](https://img.shields.io/badge/MySQL-8-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen)

---

## 📚 Descripción

**El Archivo de Vector** es una plataforma educativa (LMS) que contiene **técnicas de redacción** organizadas en **45 cursos** con **360 lecciones** y **2160 ejercicios interactivos**. Extrae automáticamente técnicas de archivos HTML y las convierte en lecciones interactivas con un diseño holográfico único.

> *"Cronista Temporal · 1000 técnicas de redacción"*

---

## 🎯 Características

| Característica | Descripción |
|----------------|-------------|
| ✅ **45 cursos** | Organizados por categorías temáticas |
| ✅ **360 lecciones** | Contenido educativo estructurado |
| ✅ **2160 ejercicios** | 5 tipos: opción múltiple, V/F, completar, ordenar, emparejar |
| ✅ **Dashboard del Profesor** | CRUD completo de ejercicios desde interfaz web |
| ✅ **Sistema de práctica** | Interactivo con retroalimentación inmediata |
| ✅ **Interfaz holográfica** | Estilo cyberpunk con efectos visuales |
| ✅ **Instalador automático** | `setup.py` para configuración rápida |
| ✅ **Generador de cursos** | Script para crear 45 cursos automáticamente |
| ✅ **Roles de usuario** | Estudiante, Profesor, Administrador |
| ✅ **Base de datos** | SQLite (desarrollo) / MySQL (producción) |
| ✅ **Panel de admin** | Gestión completa de cursos, lecciones y ejercicios |

---

## 📂 Cursos Incluidos

El generador automático crea 45 cursos, entre ellos:

| # | Curso | Lecciones |
|---|-------|-----------|
| 1 | Ortografía Avanzada | 10 |
| 2 | Gramática del Castellano | 10 |
| 3 | Figuras Retóricas | 10 |
| 4 | Sintaxis Básica | 10 |
| 5 | Semántica y Pragmática | 10 |
| 6 | Fonética y Fonología | 10 |
| 7 | Redacción Científica | 10 |
| 8 | Periodismo y Crónica | 10 |
| ... | ... | ... |
| 45 | Literatura de Viajes | 10 |

**Total:** 45 cursos · 360 lecciones · 2160 ejercicios

---

## 🚀 Instalación Rápida

### Opción 1: Instalador Automático

```bash
# Clonar el repositorio
git clone https://github.com/Hernank10/Redaccion_castellana_curso.git
cd Redaccion_castellana_curso

# Ejecutar el instalador
python setup.py
# Clonar repositorio
git clone https://github.com/Hernank10/Redaccion_castellana_curso.git
cd Redaccion_castellana_curso

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Migrar base de datos
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Generar 45 cursos
python manage.py generar_45_cursos --clean

# Iniciar servidor
python manage.py runserver
Opción 3: Script de Inicio Rápido
bash
./run.sh
📊 Comandos Útiles
Comando	Descripción
python manage.py runserver	Iniciar servidor Django
python manage.py generar_45_cursos --clean	Generar 45 cursos con lecciones y ejercicios
python manage.py generar_ejercicios_avanzados --por-leccion 10 --clean	Generar ejercicios avanzados
python show_db.py stats	Ver estadísticas de la base de datos
python show_db.py cursos	Listar todos los cursos
python show_db.py curso "Nombre"	Ver lecciones de un curso
python practicar.py	Modo práctica en terminal
 Dashboard del Profesor
El panel del profesor permite:

Ver todos los cursos con sus lecciones

Gestionar ejercicios por lección (crear, editar, eliminar)

Visualizar contenido de forma rápida

Para acceder, inicia sesión como profesor / profesor123.

🛠️ Tecnologías Utilizadas
Backend
Django 4.2.7 - Framework web

SQLite / MySQL - Base de datos

Python 3.12+ - Lenguaje principal

Frontend
HTML5 - Estructura

CSS3 - Estilos holográficos

JavaScript - Interactividad

Font Awesome - Iconos

Herramientas de Desarrollo
Git - Control de versiones

GitHub - Repositorio remoto

VS Code - Editor recomendado

📁 Estructura del Proyecto
text
Redaccion_castellana_curso/
├── core/                       # App principal
│   ├── models.py               # Modelos: Course, Lesson, Exercise, UserProgress...
│   ├── admin.py                # Panel de administración
│   ├── views.py                # Vistas (incluyendo dashboard del profesor)
│   ├── urls.py                 # Rutas URL
│   └── management/commands/    # Comandos personalizados
│       ├── generar_45_cursos.py
│       ├── generar_ejercicios_avanzados.py
│       └── agregar_ejercicios.py
├── templates/core/             # Plantillas HTML
│   ├── base.html               # Base con estilo holográfico
│   ├── index.html              # Página principal
│   ├── lesson_detail.html      # Lecciones por curso
│   ├── practice.html           # Modo práctica
│   ├── dashboard.html          # Dashboard de estudiante
│   ├── teacher_dashboard.html  # Dashboard del profesor
│   ├── teacher_lesson_detail.html
│   └── teacher_exercise_edit.html
├── static/                     # Archivos estáticos
│   ├── css/vector.css          # Estilos holográficos
│   └── js/vector.js            # JavaScript
├── data/                       # Datos y backups
├── manage.py                   # CLI de Django
├── setup.py                    # Instalador automático
├── run.sh                      # Script de inicio
├── show_db.py                  # Visualizador de BD
├── practicar.py                # Modo práctica en terminal
├── requirements.txt            # Dependencias Python
└── README.md                   # Este archivo
🔧 Desarrollo y Contribución
Cómo contribuir
Haz un fork del repositorio

Crea una rama: git checkout -b feature/mi-mejora

Haz tus cambios: git commit -m "Añadir nueva funcionalidad"

Sube los cambios: git push origin feature/mi-mejora
Abre un Pull Request

Reportar issues
Si encuentras algún problema, por favor abre un issue en:
https://github.com/Hernank10/Redaccion_castellana_curso/issues

👤 Autor
Hernank10 - Desarrollador principal - GitHub

🙏 Agradecimientos
A todos los colaboradores que han contribuido al proyecto

A los usuarios que comparten y difunden el conocimiento

"El conocimiento es la llave que abre todas las puertas"

⌛ Cronista Temporal · Archivo de Vector

🌟 ¡Dale una estrella al repositorio si te gusta!
text

---

## 🚀 PASO FINAL: Crear el README con `cat` (alternativa a nano)

Si prefieres usar `cat` para crear el archivo directamente desde la terminal:

```bash
cat > README.md << 'EOF'
[PEGA TODO EL CONTENIDO DE ARRIBA]
EOF
Pero como el contenido es muy largo, es mejor usar nano para pegarlo cómodamente.

✅ ¡LISTO!
bash
# Crear/editar README
nano README.md

# Ver el contenido
cat README.md | head -20

# Agregar a Git
git add README.md
git commit -m "📝 Actualizar README.md con documentación completa"
git push
