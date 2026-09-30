from django.core.management.base import BaseCommand
from core.models import Lesson, Exercise
import random

class Command(BaseCommand):
    help = 'Agrega ejercicios a lecciones con menos de 5'

    def handle(self, *args, **options):
        total_agregados = 0
        for lesson in Lesson.objects.filter(is_active=True):
            actuales = lesson.exercises.count()
            if actuales >= 5:
                continue
            faltantes = 5 - actuales
            root = lesson.root
            meaning = lesson.meaning
            for i in range(faltantes):
                incorrectas = [
                    f"Definición errónea {i+1}",
                    f"Significado alternativo {i+1}",
                    f"Otra definición {i+1}",
                    f"Definición incorrecta {i+1}"
                ]
                random.shuffle(incorrectas)
                opciones = [meaning[:50]] + incorrectas[:3]
                random.shuffle(opciones)
                correct_idx = opciones.index(meaning[:50])
                correct_letter = ['A', 'B', 'C', 'D'][correct_idx]
                Exercise.objects.create(
                    lesson=lesson,
                    exercise_type='multiple_choice',
                    question=f"¿Cuál es el significado de '{root}'? (Ejercicio {actuales + i + 1})",
                    option_a=opciones[0],
                    option_b=opciones[1],
                    option_c=opciones[2],
                    option_d=opciones[3] if len(opciones) > 3 else "Ninguna de las anteriores",
                    correct_answer=correct_letter,
                    explanation=f"La respuesta correcta es: {meaning[:100]}",
                    points=1
                )
                total_agregados += 1
            if faltantes > 0:
                self.stdout.write(f"✅ {lesson.title}: +{faltantes} ejercicios")
        self.stdout.write(self.style.SUCCESS(f"🎉 Total ejercicios agregados: {total_agregados}"))
