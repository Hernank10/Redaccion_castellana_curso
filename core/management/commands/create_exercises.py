import random
from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Crea ejercicios de opción múltiple a partir de las lecciones'

    def handle(self, *args, **options):
        self.stdout.write('📝 Creando ejercicios...')
        
        for course in Course.objects.all():
            lessons = course.lessons.filter(is_active=True)
            if not lessons:
                continue
            
            count = 0
            for lesson in lessons:
                # Usar la raíz como pregunta
                question = f"¿Qué significa '{lesson.root}'?"
                
                # Obtener respuestas incorrectas de otras lecciones
                other_lessons = course.lessons.exclude(id=lesson.id).filter(is_active=True)
                wrong_answers = list(other_lessons.values_list('meaning', flat=True))
                random.shuffle(wrong_answers)
                wrong_answers = wrong_answers[:3]
                
                # Si no hay suficientes, usar respuestas genéricas
                while len(wrong_answers) < 3:
                    wrong_answers.append("Significado no disponible")
                
                # Crear ejercicio (solo mostramos, no guardamos aún)
                self.stdout.write(f'  Ejercicio para: {lesson.root}')
                self.stdout.write(f'    Pregunta: {question}')
                self.stdout.write(f'    Correcta: {lesson.meaning}')
                self.stdout.write(f'    Incorrectas: {wrong_answers}')
                self.stdout.write('')
                count += 1
            
            self.stdout.write(self.style.SUCCESS(f'✅ {count} ejercicios generados para {course.name}'))
