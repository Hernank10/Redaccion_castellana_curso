"""
Generador automático de datos para el Archivo de Vector.
Crea 20 cursos, 20 lecciones por curso y ejercicios.
"""

import re
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Course, Lesson, Exercise, UserProgress, UserScore, UserStreak
from faker import Faker

fake = Faker('es_ES')

def slugify(text):
    """Convierte un texto a slug seguro para URLs."""
    text = text.lower()
    text = re.sub(r'[á]', 'a', text)
    text = re.sub(r'[é]', 'e', text)
    text = re.sub(r'[í]', 'i', text)
    text = re.sub(r'[ó]', 'o', text)
    text = re.sub(r'[ú]', 'u', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text

class Command(BaseCommand):
    help = 'Genera datos de prueba: cursos, lecciones, ejercicios y usuarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Eliminar todos los datos existentes antes de generar',
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('🧹 Eliminando datos existentes...')
            UserProgress.objects.all().delete()
            UserScore.objects.all().delete()
            UserStreak.objects.all().delete()
            Exercise.objects.all().delete()
            Lesson.objects.all().delete()
            Course.objects.all().delete()
            self.stdout.write('✅ Datos eliminados')

        self.stdout.write('🚀 Generando datos...')

        temas = [
            'Ortografía Avanzada', 'Gramática del Castellano', 'Figuras Retóricas',
            'Sintaxis Básica', 'Semántica y Pragmática', 'Fonética y Fonología',
            'Redacción Científica', 'Periodismo y Crónica', 'Literatura Hispanoamericana',
            'Poesía Castellana', 'Análisis del Discurso', 'Comunicación Efectiva',
            'Escritura Académica', 'Argumentación Jurídica', 'Narrativa Creativa',
            'Descripción y Detalle', 'Exposición de Ideas', 'Comparación y Contraste',
            'Conectores y Cohesión', 'Signos de Puntuación'
        ]

        categorias = [
            'grammar', 'syntax', 'orthography', 'rhetoric', 'narration',
            'exposition', 'argumentation', 'description', 'connectors',
            'punctuation', 'phonetics', 'periphrasis', 'comparison',
            'literature', 'poetry', 'etymology', 'communication',
            'academic', 'scientific', 'journalism'
        ]

        for i in range(20):
            tema = temas[i % len(temas)]
            categoria = categorias[i % len(categorias)]
            slug_base = slugify(tema)
            slug = f"curso-{i+1}-{slug_base}"
            course = Course.objects.create(
                slug=slug,
                name=f"{i+1}. {tema}",
                description=f"Curso completo sobre {tema.lower()} con 20 lecciones prácticas.",
                icon=random.choice(['📚', '✍️', '🎯', '🧠', '📖', '🔍', '✏️', '📝', '🎓', '💡']),
                category=categoria,
                is_active=True
            )

            for j in range(1, 21):
                lesson = Lesson.objects.create(
                    course=course,
                    order=j,
                    title=f"Lección {j}: {fake.sentence(nb_words=4)}",
                    root=f"{fake.word()}-{fake.word()}",
                    meaning=fake.paragraph(nb_sentences=2),
                    example=f"{fake.sentence()}",
                    breakdown=f"{fake.word()} + {fake.word()} → {fake.word()}",
                    difficulty=random.choice(['beginner', 'intermediate', 'advanced']),
                    duration_minutes=random.randint(3, 15),
                    is_active=True
                )

                for k in range(3):
                    Exercise.objects.create(
                        lesson=lesson,
                        exercise_type='multiple_choice',
                        question=f"Pregunta {k+1}: {fake.sentence(nb_words=6)}",
                        option_a=fake.sentence(nb_words=4),
                        option_b=fake.sentence(nb_words=4),
                        option_c=fake.sentence(nb_words=4),
                        option_d=fake.sentence(nb_words=4),
                        correct_answer=random.choice(['A', 'B', 'C', 'D']),
                        explanation=fake.paragraph(nb_sentences=1),
                        points=random.randint(1, 3)
                    )

            self.stdout.write(f'✅ Curso creado: {course.name} con {course.lessons.count()} lecciones')

        if not User.objects.filter(username='estudiante1').exists():
            User.objects.create_user('estudiante1', 'estudiante1@test.com', '123456')
            User.objects.create_user('estudiante2', 'estudiante2@test.com', '123456')
            User.objects.create_user('profesor1', 'profesor1@test.com', '123456')
            self.stdout.write('✅ Usuarios de prueba creados')

        self.stdout.write(self.style.SUCCESS('🎉 ¡Datos generados exitosamente!'))
