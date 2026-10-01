# -*- coding: utf-8 -*-
"""test_api.py - Tests de la API REST."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from core.models import Inscripcion, UserProgress
from .factories import (
    crear_user, crear_curso, crear_leccion, crear_progreso,
    crear_inscripcion, crear_score, crear_certificado, crear_notificacion,
)


class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'apiuser',
            'email': 'api@test.local',
            'password': 'Test12345',
            'first_name': 'API',
            'last_name': 'User',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)

    def test_login(self):
        crear_user(username='apilogin', password='Test1234!')
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'apilogin', 'password': 'Test1234!'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_login_incorrecto(self):
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'noexiste', 'password': 'x'
        }, format='json')
        self.assertEqual(response.status_code, 401)

    def test_me_sin_token(self):
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, 401)

    def test_me_con_token(self):
        user = crear_user(username='apime')
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'apime')

    def test_logout(self):
        user = crear_user()
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Token.objects.filter(user=user).exists())


class CourseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.curso = crear_curso(name='API Curso', slug='api-curso')

    def test_lista_publica(self):
        response = self.client.get('/api/v1/courses/')
        self.assertEqual(response.status_code, 200)

    def test_detalle_publico(self):
        response = self.client.get(f'/api/v1/courses/{self.curso.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'API Curso')

    def test_lecciones_del_curso(self):
        crear_leccion(self.curso)
        response = self.client.get(f'/api/v1/courses/{self.curso.slug}/lessons/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_ranking_curso(self):
        response = self.client.get(f'/api/v1/courses/{self.curso.slug}/ranking/')
        self.assertEqual(response.status_code, 200)


class ProgressAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = crear_user()
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.curso = crear_curso()
        self.leccion = crear_leccion(self.curso)

    def test_guardar_progreso(self):
        response = self.client.post('/api/v1/progress/guardar/', {
            'lesson_id': self.leccion.id,
            'score': 85,
            'completed': True,
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserProgress.objects.filter(
            user=self.user, lesson=self.leccion, completed=True
        ).exists())

    def test_listar_progreso(self):
        crear_progreso(self.user, self.leccion)
        response = self.client.get('/api/v1/progress/')
        self.assertEqual(response.status_code, 200)


class InscripcionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = crear_user()
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.curso = crear_curso()

    def test_inscribirse(self):
        response = self.client.post('/api/v1/inscripciones/inscribirse/', {
            'curso_slug': self.curso.slug
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Inscripcion.objects.filter(user=self.user, course=self.curso).exists())

    def test_listar(self):
        crear_inscripcion(self.user, self.curso)
        response = self.client.get('/api/v1/inscripciones/')
        self.assertEqual(response.status_code, 200)


class CertificadoAPITest(TestCase):
    def test_listar_certificados(self):
        client = APIClient()
        user = crear_user()
        curso = crear_curso()
        crear_certificado(user, curso)
        token, _ = Token.objects.get_or_create(user=user)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get('/api/v1/certificados/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)


class NotificacionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = crear_user()
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_listar(self):
        crear_notificacion(self.user, 'API Notif')
        response = self.client.get('/api/v1/notificaciones/')
        self.assertEqual(response.status_code, 200)

    def test_marcar_leida(self):
        from core.models import Notificacion
        n = crear_notificacion(self.user)
        response = self.client.post(f'/api/v1/notificaciones/{n.id}/leer/')
        self.assertEqual(response.status_code, 200)
        n.refresh_from_db()
        self.assertTrue(n.leida)

    def test_leer_todas(self):
        from core.models import Notificacion
        crear_notificacion(self.user)
        crear_notificacion(self.user)
        response = self.client.post('/api/v1/notificaciones/leer_todas/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notificacion.objects.filter(user=self.user, leida=False).count(), 0)


class RankingAPITest(TestCase):
    def test_ranking_publico(self):
        client = APIClient()
        response = client.get('/api/v1/ranking/')
        self.assertEqual(response.status_code, 200)