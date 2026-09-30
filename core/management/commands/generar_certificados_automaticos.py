"""
📜 GENERADOR AUTOMÁTICO DE CERTIFICADOS
========================================
- Genera certificados para usuarios que completan lecciones/cursos
- Verifica progreso y crea certificados automáticamente
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Lesson, Course, UserProgress, Certificado
import uuid
from datetime import datetime

class Command(BaseCommand):
    help = 'Genera certificados automáticos para usuarios con progreso completo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Nombre de usuario específico'
        )
        parser.add_argument(
            '--leccion',
            type=int,
            help='ID de lección específica'
        )
        parser.add_argument(
            '--curso',
            type=str,
            help='Slug del curso'
        )
        parser.add_argument(
            '--porcentaje',
            type=int,
            default=70,
            help='Porcentaje mínimo para certificado (por defecto 70)'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Eliminar certificados existentes antes de generar'
        )

    def handle(self, *args, **options):
        porcentaje_min = options.get('porcentaje', 70)
        usuario_nombre = options.get('usuario')
        leccion_id = options.get('leccion')
        curso_slug = options.get('curso')
        limpiar = options.get('limpiar')

        if limpiar:
            count = Certificado.objects.count()
            Certificado.objects.all().delete()
            self.stdout.write(f'🧹 Eliminados {count} certificados')

        self.stdout.write(f'📜 GENERANDO CERTIFICADOS')
        self.stdout.write(f'📊 Porcentaje mínimo: {porcentaje_min}%')
        self.stdout.write('=' * 50)

        # Obtener usuarios
        if usuario_nombre:
            usuarios = User.objects.filter(username=usuario_nombre)
        else:
            usuarios = User.objects.all()

        total_generados = 0

        for user in usuarios:
            self.stdout.write(f'\n👤 Usuario: {user.username}')

            # Verificar lecciones completadas
            if leccion_id:
                lecciones = Lesson.objects.filter(id=leccion_id, is_active=True)
            else:
                lecciones = Lesson.objects.filter(is_active=True)

            for lesson in lecciones:
                # Obtener progreso
                total_ejercicios = lesson.exercises.filter(is_active=True).count()
                if total_ejercicios == 0:
                    continue

                completados = UserProgress.objects.filter(
                    user=user, lesson=lesson, completed=True
                ).count()
                porcentaje = int((completados / total_ejercicios) * 100)

                if porcentaje >= porcentaje_min:
                    # Verificar si ya tiene certificado
                    certificado, creado = Certificado.objects.get_or_create(
                        usuario=user,
                        leccion=lesson,
                        defaults={
                            'curso': lesson.course,
                            'titulo': f"Lección: {lesson.title}",
                            'puntuacion': 100,
                            'ejercicios_completados': completados,
                            'total_ejercicios': total_ejercicios,
                            'porcentaje': porcentaje,
                            'codigo_verificacion': f"VECTOR-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:4].upper()}"
                        }
                    )

                    if creado:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✅ Certificado creado: {lesson.title[:30]}... '
                                f'({porcentaje}%)'
                            )
                        )
                        total_generados += 1
                    else:
                        self.stdout.write(
                            f'  ℹ️ Certificado ya existe: {lesson.title[:30]}...'
                        )

            # Verificar cursos completos (todas las lecciones)
            if curso_slug:
                cursos = Course.objects.filter(slug=curso_slug, is_active=True)
            else:
                cursos = Course.objects.filter(is_active=True)

            for course in cursos:
                lecciones_curso = course.lessons.filter(is_active=True)
                if not lecciones_curso:
                    continue

                total_curso = lecciones_curso.count()
                completadas_curso = UserProgress.objects.filter(
                    user=user, lesson__course=course, completed=True
                ).count()

                if total_curso > 0 and completadas_curso == total_curso:
                    # Curso completado
                    certificado, creado = Certificado.objects.get_or_create(
                        usuario=user,
                        curso=course,
                        leccion=None,
                        defaults={
                            'titulo': f"Curso: {course.name}",
                            'puntuacion': 100,
                            'ejercicios_completados': completadas_curso,
                            'total_ejercicios': total_curso,
                            'porcentaje': 100,
                            'codigo_verificacion': f"VECTOR-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:4].upper()}"
                        }
                    )

                    if creado:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✅ Certificado de curso: {course.name}'
                            )
                        )
                        total_generados += 1

        self.stdout.write('=' * 50)
        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 CERTIFICADOS GENERADOS: {total_generados}'
        ))
