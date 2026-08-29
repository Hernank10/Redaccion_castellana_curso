from django.core.management.base import BaseCommand
from core.models import Lesson, Exercise
import random

class Command(BaseCommand):
    help = 'Genera ejercicios variados (5 tipos) para cada lección'

    def add_arguments(self, parser):
        parser.add_argument(
            '--por-leccion',
            type=int,
            default=10,
            help='Número de ejercicios por lección (por defecto 10)'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Eliminar ejercicios existentes antes de generar'
        )

    def handle(self, *args, **options):
        por_leccion = options['por_leccion']
        clean = options['clean']

        if clean:
            self.stdout.write('🧹 Eliminando ejercicios existentes...')
            count = Exercise.objects.count()
            Exercise.objects.all().delete()
            self.stdout.write(f'✅ {count} ejercicios eliminados')

        self.stdout.write(f'📚 Generando {por_leccion} ejercicios por lección...')

        lecciones = Lesson.objects.filter(is_active=True)
        total_creados = 0

        for lesson in lecciones:
            # Tipos de ejercicios para alternar
            tipos = ['multiple_choice', 'true_false', 'completar', 'ordenar', 'emparejar']
            for i in range(por_leccion):
                tipo = tipos[i % len(tipos)]
                ejercicio = self.generar_ejercicio(lesson, tipo, i)
                if ejercicio:
                    ejercicio['lesson_id'] = lesson.id
                    Exercise.objects.create(**ejercicio)
                    total_creados += 1

            self.stdout.write(f'✅ {lesson.title}: {por_leccion} ejercicios generados')

        self.stdout.write(self.style.SUCCESS(f'🎉 Total ejercicios creados: {total_creados}'))

    def generar_ejercicio(self, lesson, tipo, idx):
        """Genera un ejercicio según el tipo"""
        root = lesson.root or 'palabra'
        meaning = lesson.meaning or 'significado'
        example = lesson.example or ''

        if tipo == 'multiple_choice':
            return {
                'exercise_type': 'multiple_choice',
                'question': f"¿Cuál es el significado de '{root}'?",
                'option_a': meaning[:100],
                'option_b': f"Definición incorrecta {idx+1}",
                'option_c': f"Definición errónea {idx+1}",
                'option_d': f"Otro significado {idx+1}",
                'correct_answer': 'A',
                'explanation': f"La respuesta correcta es: {meaning[:100]}",
                'points': 1,
            }

        elif tipo == 'true_false':
            # Verdadero o falso: la afirmación puede ser verdadera o falsa
            es_verdadero = random.choice([True, False])
            if es_verdadero:
                pregunta = f"La raíz '{root}' significa '{meaning[:30]}'."
                correcto = 'V'
                explicacion = f"Correcto. '{root}' significa '{meaning[:30]}'."
            else:
                # Generar significado falso
                falsos = ['casa', 'perro', 'tiempo', 'luz', 'oscuridad']
                falso = random.choice(falsos)
                pregunta = f"La raíz '{root}' significa '{falso}'."
                correcto = 'F'
                explicacion = f"Incorrecto. '{root}' significa '{meaning[:30]}', no '{falso}'."

            return {
                'exercise_type': 'true_false',
                'question': pregunta,
                'option_a': 'Verdadero',
                'option_b': 'Falso',
                'option_c': '',
                'option_d': '',
                'correct_answer': correcto,
                'explanation': explicacion,
                'points': 1,
            }

        elif tipo == 'completar':
            # Completar: falta una palabra en la definición
            palabras = meaning.split()
            if len(palabras) > 2:
                pos = random.randint(1, len(palabras)-2)
                palabra_oculta = palabras[pos]
                palabras[pos] = '________'
                pregunta = f"Completa la definición de '{root}':\n{' '.join(palabras)}"
                return {
                    'exercise_type': 'fill_blank',
                    'question': pregunta,
                    'option_a': palabra_oculta,
                    'option_b': f'Palabra {idx+1}',
                    'option_c': f'Palabra {idx+2}',
                    'option_d': f'Palabra {idx+3}',
                    'correct_answer': 'A',
                    'explanation': f"La palabra correcta es '{palabra_oculta}'",
                    'points': 1,
                }
            else:
                # Si no se puede, crear opción múltiple simple
                return self.generar_ejercicio(lesson, 'multiple_choice', idx)

        elif tipo == 'ordenar':
            # Ordenar: se muestra un conjunto de palabras desordenadas
            palabras = ['una', 'frase', 'ejemplo', 'ordenar']
            random.shuffle(palabras)
            pregunta = f"Ordena correctamente las palabras: {' '.join(palabras)}"
            correcto = ' '.join(['una', 'frase', 'ejemplo', 'ordenar'])
            return {
                'exercise_type': 'matching',
                'question': pregunta,
                'option_a': correcto,
                'option_b': f'Orden incorrecto {idx+1}',
                'option_c': f'Orden incorrecto {idx+2}',
                'option_d': f'Orden incorrecto {idx+3}',
                'correct_answer': 'A',
                'explanation': f"El orden correcto es: {correcto}",
                'points': 1,
            }

        elif tipo == 'emparejar':
            # Emparejar: definir con significado
            return {
                'exercise_type': 'matching',
                'question': f"Empareja '{root}' con su significado.",
                'option_a': meaning[:100],
                'option_b': f"Definición incorrecta {idx+1}",
                'option_c': f"Definición errónea {idx+1}",
                'option_d': f"Definición incorrecta {idx+2}",
                'correct_answer': 'A',
                'explanation': f"'{root}' significa: {meaning[:100]}",
                'points': 1,
            }

        return None
