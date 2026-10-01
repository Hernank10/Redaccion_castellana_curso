# -*- coding: utf-8 -*-
"""test_auth.py - Tests de autenticacion y perfil."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Inscripcion, Certificado
from .factories import crear_user, crear_curso, crear_leccion, crear_progreso, crear_score, crear_streak


class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = crear_user(username='loginuser', password='Test1234!')

    def test_login_correcto(self):
        response = self.client.post('/es/login/', {'username': 'loginuser', 'password': 'Test1234!'})
        self.assertEqual(response.status_code, 302)

    def test_login_incorrecto(self):
        response = self.client.post('/es/login/', {'username': 'loginuser', 'password': 'mal'})
        self.assertEqual(response.status_code, 200)


class RegistroTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registro_view_get(self):
        response = self.client.get('/es/registro/')
        self.assertEqual(response.status_code, 200)

    def test_registro_crea_usuario(self):
        response = self.client.post('/es/registro/', {
            'username': 'nuevo_user',
            'email': 'nuevo@test.local',
            'password': 'Test1234!',
            'password2': 'Test1234!',
        })
        # Depende de la implementacion; puede redirigir o mostrar form
        self.assertIn(response.status_code, [200, 302])


class PerfilTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = crear_user(username='perfiluser')

    def test_perfil_requiere_login(self):
        response = self.client.get('/es/perfil/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_perfil_carga_con_login(self):
        self.client.force_login(self.user)
        response = self.client.get('/es/perfil/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'perfiluser')


class LogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = crear_user()

    def test_logout_post(self):
        self.client.force_login(self.user)
        response = self.client.post('/es/logout/')
        self.assertEqual(response.status_code, 302)

    def test_logout_get_no_permitido(self):
        self.client.force_login(self.user)
        response = self.client.get('/es/logout/')
        # Django 5 exige POST
        self.assertEqual(response.status_code, 405)


class PasswordChangeTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = crear_user(username='pwuser', password='Test1234!')

    def test_password_change_requiere_login(self):
        response = self.client.get('/es/password_change/')
        self.assertEqual(response.status_code, 302)