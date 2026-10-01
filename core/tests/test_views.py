# -*- coding: utf-8 -*-
"""test_views.py - Tests de vistas principales."""
from django.test import TestCase, Client
from core.models import Inscripcion, Notificacion
from .factories import (
    crear_user, crear_curso, crear_leccion, crear_progreso,
    crear_inscripcion, crear_score, crear_streak, crear_notificacion,
)


class IndexTest(TestCase):
    def test_home_redirige(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)


class CourseListTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.curso = crear_curso()

    def test_course_list_carga(self):
        response = self.client.get('/es/cursos/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Curso Test')


class CourseDetailTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = crear_user()
        self.curso = crear_curso()
        self.leccion = crear_leccion(self.curso)

    def test_course_detail_carga(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/es/curso/{self.curso.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Curso Test')

    def test_inscripcion_automatica(self):
        self.client.force_login(self.user)
        self.client.get(f'/es/curso/{self.curso.slug}/')
        self.assertTrue(Inscripcion.objects.filter(user=self.user, course=self.curso).exists())


class DashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = crear_user(username='dashuser')
        self.curso = crear_curso()
        self.leccion = crear_leccion(self.curso)

    def test_dashboard_requiere_login(self):
        response = self.client.get('/es/dashboard/')
        self.assertEqual(response.status_code, 302)

    def test_dashboard_con_login(self):
        self.client.force_login(self.user)
        response = self.client.get('/es/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_muestra_estadisticas(self):
        self.client.force_login(self.user)
        crear_score(self.user, points=500)
        crear_streak(self.user, streak=5)
        crear_inscripcion(self.user, self.curso)
        response = self.client.get('/es/dashboard/')
        self.assertContains(response, '500')


class NotificacionesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = crear_user()

    def test_lista_requiere_login(self):
        response = self.client.get('/es/notificaciones/')
        self.assertEqual(response.status_code, 302)

    def test_lista_con_login(self):
        self.client.force_login(self.user)
        crear_notificacion(self.user, 'Test notif')
        response = self.client.get('/es/notificaciones/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test notif')

    def test_marcar_leida(self):
        self.client.force_login(self.user)
        notif = crear_notificacion(self.user)
        response = self.client.get(f'/es/notificaciones/leer/{notif.id}/')
        notif.refresh_from_db()
        self.assertTrue(notif.leida)

    def test_marcar_todas(self):
        self.client.force_login(self.user)
        crear_notificacion(self.user)
        crear_notificacion(self.user)
        self.client.get('/es/notificaciones/marcar-todas/')
        self.assertEqual(Notificacion.objects.filter(user=self.user, leida=False).count(), 0)


class BuscarTest(TestCase):
    def setUp(self):
        self.curso = crear_curso(name='Curso Buscable', slug='curso-buscable')

    def test_buscar_sin_query(self):
        response = self.client.get('/es/buscar/')
        self.assertEqual(response.status_code, 200)

    def test_buscar_con_query(self):
        response = self.client.get('/es/buscar/?q=Buscable')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Curso Buscable')

    def test_buscar_sin_resultados(self):
        response = self.client.get('/es/buscar/?q=xyzabc123')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No se encontraron resultados')


class RankingTest(TestCase):
    def setUp(self):
        self.user = crear_user()
        crear_score(self.user, points=999)

    def test_ranking_global(self):
        response = self.client.get('/es/ranking/')
        self.assertEqual(response.status_code, 200)

    def test_ranking_curso(self):
        curso = crear_curso()
        response = self.client.get(f'/es/ranking/curso/{curso.slug}/')
        self.assertEqual(response.status_code, 200)


class TeacherViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.profe = crear_user(username='profex', is_staff=True)
        self.curso = crear_curso()
        self.curso.teachers.add(self.profe)

    def test_teacher_dashboard_sin_staff(self):
        user = crear_user(username='normal')
        self.client.force_login(user)
        response = self.client.get('/es/profesor/')
        self.assertEqual(response.status_code, 302)

    def test_teacher_dashboard_con_staff(self):
        self.client.force_login(self.profe)
        response = self.client.get('/es/profesor/')
        self.assertEqual(response.status_code, 200)

    def test_teacher_course_students(self):
        self.client.force_login(self.profe)
        response = self.client.get(f'/es/profesor/curso/{self.curso.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_teacher_course_edit_get(self):
        self.client.force_login(self.profe)
        response = self.client.get(f'/es/profesor/curso/{self.curso.slug}/editar/')
        self.assertEqual(response.status_code, 200)