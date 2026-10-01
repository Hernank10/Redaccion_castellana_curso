# -*- coding: utf-8 -*-
"""test_models.py - Tests de modelos."""
from django.test import TestCase
from core.models import (
    Course, Lesson, UserProgress, Inscripcion, Certificado, Logro, Evaluacion, Notificacion
)
from .factories import (
    crear_user, crear_curso, crear_leccion, crear_ejercicio,
    crear_progreso, crear_inscripcion, crear_certificado, crear_logro,
    crear_evaluacion, crear_notificacion, crear_profesor,
)


class CourseModelTest(TestCase):
    def setUp(self):
        self.curso = crear_curso()

    def test_crear_curso(self):
        self.assertEqual(self.curso.name, 'Curso Test')
        self.assertEqual(self.curso.slug, 'curso-test')
        self.assertTrue(self.curso.is_active)

    def test_str(self):
        self.assertEqual(str(self.curso), 'Curso Test')

    def test_lecciones_relacionadas(self):
        crear_leccion(self.curso, order=1)
        crear_leccion(self.curso, order=2, title='Leccion 2')
        self.assertEqual(self.curso.lessons.count(), 2)

    def test_teachers_m2m(self):
        profe = crear_profesor()
        self.curso.teachers.add(profe)
        self.assertIn(profe, self.curso.teachers.all())


class LessonModelTest(TestCase):
    def setUp(self):
        self.curso = crear_curso()
        self.leccion = crear_leccion(self.curso)

    def test_crear_leccion(self):
        self.assertEqual(self.leccion.title, 'Leccion 1')
        self.assertEqual(self.leccion.course, self.curso)

    def test_ejercicios_relacionados(self):
        crear_ejercicio(self.leccion)
        crear_ejercicio(self.leccion, question='Otra')
        self.assertEqual(self.leccion.exercises.count(), 2)


class UserProgressModelTest(TestCase):
    def setUp(self):
        self.user = crear_user()
        self.curso = crear_curso()
        self.leccion = crear_leccion(self.curso)

    def test_crear_progreso(self):
        prog = crear_progreso(self.user, self.leccion)
        self.assertTrue(prog.completed)
        self.assertEqual(prog.score, 80)

    def test_unique_user_lesson(self):
        crear_progreso(self.user, self.leccion)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            UserProgress.objects.create(user=self.user, lesson=self.leccion, score=50)


class InscripcionModelTest(TestCase):
    def setUp(self):
        self.user = crear_user()
        self.curso = crear_curso()

    def test_crear_inscripcion(self):
        insc = crear_inscripcion(self.user, self.curso)
        self.assertEqual(insc.user, self.user)
        self.assertEqual(insc.course, self.curso)

    def test_unique_user_course(self):
        crear_inscripcion(self.user, self.curso)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Inscripcion.objects.create(user=self.user, course=self.curso)


class CertificadoModelTest(TestCase):
    def setUp(self):
        self.user = crear_user()
        self.curso = crear_curso()

    def test_crear_certificado(self):
        cert = crear_certificado(self.user, self.curso)
        self.assertEqual(cert.usuario, self.user)
        self.assertEqual(cert.porcentaje, 100)
        self.assertTrue(cert.codigo_verificacion.startswith('TEST-'))

    def test_str(self):
        cert = crear_certificado(self.user, self.curso)
        self.assertIn(self.user.username, str(cert))


class LogroModelTest(TestCase):
    def test_crear_logro(self):
        user = crear_user()
        logro = crear_logro(user)
        self.assertEqual(logro.tipo, 'medalla')
        self.assertEqual(logro.icono, '🏅')


class EvaluacionModelTest(TestCase):
    def test_crear_evaluacion(self):
        profe = crear_profesor()
        estudiante = crear_user()
        curso = crear_curso()
        ev = crear_evaluacion(profe, estudiante, curso, nota=90)
        self.assertEqual(ev.nota, 90)
        self.assertEqual(ev.profesor, profe)


class NotificacionModelTest(TestCase):
    def test_crear_notificacion(self):
        user = crear_user()
        n = crear_notificacion(user)
        self.assertFalse(n.leida)
        self.assertEqual(n.tipo, 'info')

    def test_orden_por_fecha_desc(self):
        user = crear_user()
        n1 = crear_notificacion(user, 'Primera')
        n2 = crear_notificacion(user, 'Segunda')
        qs = list(Notificacion.objects.filter(user=user))
        self.assertEqual(qs[0].id, n2.id)