# -*- coding: utf-8 -*-
"""factories.py - Datos de prueba reutilizables."""
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import (
    Course, Lesson, Exercise, UserProgress, UserScore, UserStreak,
    Certificado, Inscripcion, Logro, Evaluacion, Notificacion,
)


def crear_user(username='test_user', password='Test1234!', **kwargs):
    defaults = {
        'email': f'{username}@test.local',
        'first_name': 'Test',
        'last_name': 'User',
    }
    defaults.update(kwargs)
    user = User.objects.create_user(username=username, password=password, **defaults)
    return user


def crear_admin(username='admin_test'):
    return User.objects.create_superuser(username=username, password='Test1234!', email=f'{username}@test.local')


def crear_profesor(username='profe_test'):
    return User.objects.create_user(
        username=username, password='Test1234!',
        email=f'{username}@test.local', is_staff=True
    )


def crear_curso(slug='curso-test', name='Curso Test', **kwargs):
    defaults = {'icon': '📚', 'category': 'grammar', 'is_active': True}
    defaults.update(kwargs)
    return Course.objects.create(slug=slug, name=name, **defaults)


def crear_leccion(curso, order=1, title='Leccion 1', **kwargs):
    defaults = {'meaning': 'Significado de prueba', 'example': 'Ejemplo de prueba', 'difficulty': 'beginner', 'is_active': True, 'duration_minutes': 10}
    defaults.update(kwargs)
    return Lesson.objects.create(course=curso, order=order, title=title, **defaults)


def crear_ejercicio(leccion, question='¿Pregunta?'):
    return Exercise.objects.create(
        lesson=leccion, question=question,
        option_a='A', option_b='B', option_c='C', option_d='D',
        correct_answer='a', is_active=True,
    )


def crear_progreso(user, leccion, completed=True, score=80):
    return UserProgress.objects.create(
        user=user, lesson=leccion, completed=completed, score=score
    )


def crear_inscripcion(user, curso):
    return Inscripcion.objects.create(user=user, course=curso)


def crear_score(user, points=100, lessons=5):
    return UserScore.objects.create(user=user, total_points=points, lessons_completed=lessons)


def crear_streak(user, streak=3):
    return UserStreak.objects.create(user=user, current_streak=streak)


def crear_certificado(user, curso):
    import uuid
    return Certificado.objects.create(
        usuario=user, curso=curso,
        titulo=f'Curso: {curso.name}',
        codigo_verificacion=f'TEST-{uuid.uuid4().hex[:8].upper()}',
        porcentaje=100, puntuacion=90,
        total_ejercicios=10, ejercicios_completados=10,
    )


def crear_logro(user, nombre='Logro Test', tipo='medalla'):
    return Logro.objects.create(user=user, tipo=tipo, nombre=nombre, icono='🏅')


def crear_evaluacion(profesor, estudiante, curso, nota=85):
    return Evaluacion.objects.create(
        profesor=profesor, estudiante=estudiante, curso=curso,
        nota=nota, comentario='Buen trabajo'
    )


def crear_notificacion(user, titulo='Notif Test', tipo='info'):
    return Notificacion.objects.create(user=user, tipo=tipo, titulo=titulo)