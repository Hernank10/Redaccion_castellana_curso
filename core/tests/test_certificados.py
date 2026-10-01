# -*- coding: utf-8 -*-
"""test_certificados.py - Tests de generacion de certificados."""
from django.test import TestCase
from django.utils import timezone
from core.certificados import generar_pdf_certificado
from .factories import crear_user, crear_curso, crear_profesor


class CertificadoPDFTest(TestCase):
    def setUp(self):
        self.user = crear_user(username='certuser', first_name='Juan', last_name='Perez')
        self.curso = crear_curso()
        self.profe = crear_profesor()
        self.curso.teachers.add(self.profe)

    def test_generar_pdf_ok(self):
        pdf = generar_pdf_certificado(
            user=self.user,
            curso=self.curso,
            completados=10,
            total=10,
            porcentaje=100,
            puntuacion=950,
            codigo='TEST-ABC123',
            fecha=timezone.now(),
        )
        contenido = pdf.read()
        self.assertGreater(len(contenido), 1000)
        self.assertTrue(contenido.startswith(b'%PDF'))

    def test_pdf_sin_profesor(self):
        curso_sin_profe = crear_curso(slug='curso-sin-profe', name='Sin Profe')
        pdf = generar_pdf_certificado(
            user=self.user, curso=curso_sin_profe,
            completados=5, total=10, porcentaje=50,
            puntuacion=400, codigo='TEST-XYZ', fecha=timezone.now(),
        )
        self.assertGreater(len(pdf.read()), 1000)

    def test_pdf_con_datos_minimos(self):
        pdf = generar_pdf_certificado(
            user=self.user, curso=self.curso,
            completados=0, total=0, porcentaje=0,
            puntuacion=0, codigo='TEST-0', fecha=timezone.now(),
        )
        self.assertGreater(len(pdf.read()), 1000)