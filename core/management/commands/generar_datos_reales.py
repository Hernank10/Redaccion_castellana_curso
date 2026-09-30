from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Course, Lesson, Exercise
import random
import unicodedata
import re

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-zA-Z0-9]+', '-', text).lower().strip('-')

class Command(BaseCommand):
    help = 'Genera datos con contenido REAL'

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true', help='Eliminar datos existentes')

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('🧹 Eliminando datos existentes...')
            Exercise.objects.all().delete()
            Lesson.objects.all().delete()
            Course.objects.all().delete()
            self.stdout.write('✅ Datos eliminados')

        self.stdout.write('📚 Generando contenido REAL...')

        contenido = {
            'Ortografía Avanzada': [
                ('Uso de la b', 'Se escribe b antes de consonante', 'blanco, brazo, abrir', 'Regla ortográfica'),
                ('Uso de la v', 'Se escribe v después de n', 'envase, invierno, enviar', 'Regla ortográfica'),
                ('Palabras agudas', 'Llevan tilde al final en vocal, n o s', 'camión, corazón, reloj', 'Acentuación'),
                ('Palabras graves', 'Llevan tilde si NO terminan en vocal, n o s', 'árbol, lápiz, fácil', 'Acentuación'),
                ('Palabras esdrújulas', 'Siempre llevan tilde', 'pájaro, médico, teléfono', 'Acentuación'),
            ],
            'Gramática del Castellano': [
                ('El sustantivo', 'Nombra personas, animales, cosas o ideas', 'Juan, perro, casa', 'Categoría gramatical'),
                ('El adjetivo', 'Acompaña al sustantivo y expresa cualidades', 'grande, pequeño, rojo', 'Categoría gramatical'),
                ('El verbo', 'Expresa acción, estado o proceso', 'correr, ser, estar', 'Categoría gramatical'),
                ('El adverbio', 'Modifica al verbo, adjetivo u otro adverbio', 'bien, mal, aquí', 'Categoría gramatical'),
                ('La preposición', 'Relaciona elementos de la oración', 'a, de, en, para', 'Categoría gramatical'),
            ],
            'Figuras Retóricas': [
                ('Metáfora', 'Comparación implícita entre dos términos', 'El tiempo es oro', 'Figura retórica'),
                ('Símil', 'Comparación explícita con "como"', 'Brillaba como el sol', 'Figura retórica'),
                ('Hipérbole', 'Exageración intencionada', 'Pesaba una tonelada', 'Figura retórica'),
                ('Ironía', 'Decir lo contrario de lo que se piensa', '¡Qué buen día! (lloviendo)', 'Figura retórica'),
                ('Antítesis', 'Contraposición de ideas contrarias', 'Eres la luz y la sombra', 'Figura retórica'),
            ],
        }

        for nombre, lecciones_data in contenido.items():
            slug = slugify(nombre)
            course = Course.objects.create(
                slug=slug,
                name=nombre,
                description=f"Curso sobre {nombre.lower()}",
                icon=random.choice(['📚', '✍️', '🎯', '📖']),
                category='general',
                is_active=True
            )

            for i, (root, meaning, example, breakdown) in enumerate(lecciones_data, 1):
                lesson = Lesson.objects.create(
                    course=course,
                    order=i,
                    title=root[:50],
                    root=root[:100],
                    meaning=meaning[:300],
                    example=example[:300] if example else '',
                    breakdown=breakdown[:300] if breakdown else '',
                    difficulty='intermediate',
                    duration_minutes=5,
                    is_active=True
                )

                # Crear 3 ejercicios por lección
                for j in range(3):
                    Exercise.objects.create(
                        lesson=lesson,
                        exercise_type='multiple_choice',
                        question=f"¿Cuál es el significado de '{root}'?",
                        option_a=meaning[:50],
                        option_b=f"Definición incorrecta {j+1}",
                        option_c=f"Definición errónea {j+1}",
                        option_d=f"Otro significado {j+1}",
                        correct_answer='A',
                        explanation=f"La respuesta correcta es: {meaning[:100]}",
                        points=1
                    )

            self.stdout.write(f'✅ Curso: {course.name} - {course.lessons.count()} lecciones')

        # Crear usuario profesor
        if not User.objects.filter(username='profesor').exists():
            user = User.objects.create_user('profesor', 'profesor@vector.com', 'profesor123')
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write('✅ Profesor creado: profesor / profesor123')

        self.stdout.write(self.style.SUCCESS('🎉 Contenido REAL generado exitosamente!'))
