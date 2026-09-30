# -*- coding: utf-8 -*-
r"""seed_usuarios.py - Verifica/crea usuarios de prueba.

Uso:
    E:\PythonPortable_Django5\python.exe run.py shell < scripts\data\seed_usuarios.py

O directamente:
    E:\PythonPortable_Django5\python.exe scripts\data\seed_usuarios.py

Modo:
    --verificar   Solo cuenta, no crea
    --crear       Crea los que falten
    --reset       Borra todos los de prueba y vuelve a crear
"""
import os
import sys
import random
import django

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_vector.settings")
django.setup()

from django.contrib.auth.models import User, Group
from django.utils import timezone
from core.models import (
    Course, Lesson, Inscripcion, UserProgress, UserScore,
    UserStreak, Certificado, Logro
)


# ============================================================
# CONFIGURACION
# ============================================================
N_ADMINS = 3
N_PROFESORES = 9
N_ESTUDIANTES = 96
N_CERTIFICADOS = 40     # cuantos estudiantes tendran certificado
N_CURSOS_INSCRITOS = 30 # cuantos cursos tendra cada estudiante

PASSWORD = "Test1234!"

# Prefijos para identificar usuarios de prueba
PREFIJO_ADMIN = "admin_test_"
PREFIJO_PROFE = "profe_test_"
PREFIJO_EST = "est_test_"


# ============================================================
# HELPERS
# ============================================================
def contar_existentes():
    return {
        "admins": User.objects.filter(username__startswith=PREFIJO_ADMIN).count(),
        "profesores": User.objects.filter(username__startswith=PREFIJO_PROFE).count(),
        "estudiantes": User.objects.filter(username__startswith=PREFIJO_EST).count(),
        "total_users": User.objects.count(),
        "cursos": Course.objects.count(),
        "lecciones": Lesson.objects.count(),
        "inscripciones": Inscripcion.objects.count(),
        "certificados": Certificado.objects.count(),
        "logros": Logro.objects.count(),
    }


def imprimir_estado(titulo, datos):
    print("")
    print("=" * 60)
    print(titulo)
    print("=" * 60)
    for k, v in datos.items():
        print(f"  {k:20s}: {v}")
    print("=" * 60)


def crear_admin(n):
    username = f"{PREFIJO_ADMIN}{n:02d}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": f"{username}@test.local",
            "first_name": f"Admin",
            "last_name": f"Test {n}",
            "is_staff": True,
            "is_superuser": True,
        }
    )
    if created:
        user.set_password(PASSWORD)
        user.save()
    return user, created


def crear_profesor(n):
    username = f"{PREFIJO_PROFE}{n:02d}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": f"{username}@test.local",
            "first_name": f"Profesor",
            "last_name": f"Test {n}",
            "is_staff": True,
        }
    )
    if created:
        user.set_password(PASSWORD)
        user.save()
    return user, created


def crear_estudiante(n):
    username = f"{PREFIJO_EST}{n:03d}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": f"{username}@test.local",
            "first_name": f"Estudiante",
            "last_name": f"Test {n}",
        }
    )
    if created:
        user.set_password(PASSWORD)
        user.save()
    return user, created


def inscribir_en_cursos(user, cursos, n_cursos):
    """Inscribe al usuario en n_cursos aleatorios."""
    seleccion = random.sample(list(cursos), min(n_cursos, len(cursos)))
    inscritos = 0
    for curso in seleccion:
        _, created = Inscripcion.objects.get_or_create(user=user, course=curso)
        if created:
            inscritos += 1
    return inscritos


def progresar_curso(user, curso, porcentaje):
    """Marca lecciones como completadas segun porcentaje (0-100)."""
    lecciones = list(curso.lessons.all())
    if not lecciones:
        return 0
    n_completar = int(len(lecciones) * porcentaje / 100)
    completadas = 0
    for leccion in lecciones[:n_completar]:
        _, created = UserProgress.objects.get_or_create(
            user=user,
            lesson=leccion,
            defaults={"completed": True, "score": random.randint(70, 100)}
        )
        if created:
            completadas += 1
    return completadas


def crear_certificado(user, curso):
    """Crea un certificado para user+curso."""
    import uuid
    codigo = f"CERT-{uuid.uuid4().hex[:8].upper()}"
    cert, created = Certificado.objects.get_or_create(
        usuario=user,
        curso=curso,
        defaults={
            "titulo": f"Certificado: {curso.name}",
            "codigo_verificacion": codigo,
            "porcentaje": 100,
            "puntuacion": random.randint(85, 100),
            "total_ejercicios": 10,
            "ejercicios_completados": 10,
        }
    )
    return cert, created


def cmd_verificar():
    datos = contar_existentes()
    imprimir_estado("ESTADO ACTUAL DE LA DB", datos)

    esperado = {
        "admins": N_ADMINS,
        "profesores": N_PROFESORES,
        "estudiantes": N_ESTUDIANTES,
    }
    print("")
    print("COMPARACION vs ESPERADO:")
    for k, v in esperado.items():
        actual = datos[k]
        estado = "OK" if actual >= v else f"FALTAN {v - actual}"
        print(f"  {k:15s}: {actual}/{v}  [{estado}]")


def cmd_crear():
    print("CREANDO USUARIOS DE PRUEBA")
    print("=" * 60)

    # 1. Cursos
    cursos = list(Course.objects.filter(is_active=True))
    if not cursos:
        print("ERROR: no hay cursos. Ejecuta primero los scripts de datos.")
        return
    print(f"Cursos disponibles: {len(cursos)}")

    # 2. Admins
    print("")
    print(f"[1] Creando {N_ADMINS} admins...")
    for i in range(1, N_ADMINS + 1):
        _, created = crear_admin(i)
        print(f"  {PREFIJO_ADMIN}{i:02d} {'[nuevo]' if created else '[ya existe]'}")

    # 3. Profesores
    print("")
    print(f"[2] Creando {N_PROFESORES} profesores...")
    for i in range(1, N_PROFESORES + 1):
        _, created = crear_profesor(i)
        print(f"  {PREFIJO_PROFE}{i:02d} {'[nuevo]' if created else '[ya existe]'}")

    # 4. Estudiantes
    print("")
    print(f"[3] Creando {N_ESTUDIANTES} estudiantes...")
    estudiantes = []
    for i in range(1, N_ESTUDIANTES + 1):
        user, created = crear_estudiante(i)
        estudiantes.append(user)
        if created and i % 20 == 0:
            print(f"  ...{i}/{N_ESTUDIANTES} creados")

    # 5. Inscripciones + progreso
    print("")
    print(f"[4] Inscribiendo cada estudiante en {N_CURSOS_INSCRITOS} cursos...")
    total_inscripciones = 0
    for i, user in enumerate(estudiantes, 1):
        n = inscribir_en_cursos(user, cursos, N_CURSOS_INSCRITOS)
        total_inscripciones += n
        if i % 20 == 0:
            print(f"  ...{i}/{N_ESTUDIANTES} estudiantes ({total_inscripciones} inscripciones)")

    # 6. Progreso aleatorio
    print("")
    print("[5] Generando progreso aleatorio...")
    for i, user in enumerate(estudiantes, 1):
        inscripciones = Inscripcion.objects.filter(user=user)
        for insc in inscripciones:
            porcentaje = random.choice([0, 10, 25, 50, 75, 100])
            progresar_curso(user, insc.course, porcentaje)
        if i % 20 == 0:
            print(f"  ...{i}/{N_ESTUDIANTES} estudiantes")

    # 7. Certificados (40 estudiantes)
    print("")
    print(f"[6] Creando certificados para {N_CERTIFICADOS} estudiantes...")
    estudiantes_cert = random.sample(estudiantes, min(N_CERTIFICADOS, len(estudiantes)))
    total_certs = 0
    for i, user in enumerate(estudiantes_cert, 1):
        # Cada estudiante con certificado obtiene 1-3 certificados
        n_certs = random.randint(1, 3)
        inscripciones = list(Inscripcion.objects.filter(user=user))
        if not inscripciones:
            continue
        for insc in random.sample(inscripciones, min(n_certs, len(inscripciones))):
            _, created = crear_certificado(user, insc.course)
            if created:
                total_certs += 1
        if i % 10 == 0:
            print(f"  ...{i}/{N_CERTIFICADOS} estudiantes ({total_certs} certificados)")

    # 8. Logros
    print("")
    print("[7] Generando logros aleatorios...")
    tipos = ["insignia", "medalla", "estrella", "libro"]
    iconos = {"insignia": "🏅", "medalla": "🥇", "estrella": "⭐", "libro": "📖"}
    total_logros = 0
    for user in estudiantes:
        n_logros = random.randint(0, 3)
        for _ in range(n_logros):
            tipo = random.choice(tipos)
            Logro.objects.create(
                user=user,
                tipo=tipo,
                nombre=f"Logro de prueba {random.randint(1, 100)}",
                descripcion="Generado automáticamente para testing",
                icono=iconos[tipo],
            )
            total_logros += 1

    # Resumen final
    print("")
    datos = contar_existentes()
    imprimir_estado("RESUMEN FINAL", datos)
    print("")
    print(f"Password para todos: {PASSWORD}")
    print(f"Ejemplo login: {PREFIJO_EST}001 / {PASSWORD}")


def cmd_reset():
    print("BORRANDO USUARIOS DE PRUEBA...")
    qs = User.objects.filter(
        username__startswith=PREFIJO_ADMIN
    ) | User.objects.filter(
        username__startswith=PREFIJO_PROFE
    ) | User.objects.filter(
        username__startswith=PREFIJO_EST
    )
    total = qs.count()
    qs.delete()
    print(f"Borrados: {total} usuarios (+ inscripciones, progreso, certificados)")


# ============================================================
# MAIN
# ============================================================
def main():
    random.seed(42)  # resultados reproducibles
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--verificar"]

    if "--verificar" in args:
        cmd_verificar()
    elif "--crear" in args:
        cmd_crear()
    elif "--reset" in args:
        cmd_reset()
    else:
        print("Uso:")
        print("  python seed_usuarios.py --verificar")
        print("  python seed_usuarios.py --crear")
        print("  python seed_usuarios.py --reset")


if __name__ == "__main__":
    main()