from django.core.management.base import BaseCommand
from core.models import Lesson, Exercise
import random

class Command(BaseCommand):
    help = 'Agrega 5 ejercicios variados a cada lección'

    def handle(self, *args, **options):
        lecciones = Lesson.objects.filter(is_active=True)
        total_agregados = 0

        preguntas = [
            "¿Qué significa la raíz '{}'?",
            "Selecciona la definición correcta para '{}'.",
            "¿Cuál es el significado de '{}'?",
            "Indica la opción que describe mejor '{}'.",
            "Identifica el significado de '{}'.",
        ]

        for lesson in lecciones:
            actuales = lesson.exercises.count()
            if actuales >= 5:
                continue

            faltantes = 5 - actuales
            root = lesson.root
            meaning = lesson.meaning

            for i in range(faltantes):
                # Elegir una pregunta aleatoria
                pregunta = preguntas[i % len(preguntas)].format(root)

                Exercise.objects.create(
                    lesson=lesson,
                    exercise_type='multiple_choice',
                    question=pregunta,
                    option_a=meaning[:50],
                    option_b=f"Definición incorrecta {i+1}",
                    option_c=f"Definición errónea {i+1}",
                    option_d=f"Otro significado {i+1}",
                    correct_answer='A',
                    explanation=f"La respuesta correcta es: {meaning[:100]}",
                    points=1
                )
                total_agregados += 1

            self.stdout.write(f"✅ {lesson.title}: +{faltantes} ejercicios")

        self.stdout.write(self.style.SUCCESS(f"🎉 Total ejercicios agregados: {total_agregados}"))
