"""
🔧 CORRECTOR AUTOMÁTICO DE EJERCICIOS
======================================
- Corrige preguntas duplicadas y mal formateadas
- Añade 5 tipos de preguntas variadas
- Mejora la calidad de los ejercicios
"""

from django.core.management.base import BaseCommand
from core.models import Lesson, Exercise
import random
import re

class Command(BaseCommand):
    help = 'Corrige automáticamente los ejercicios de todas las lecciones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--leccion',
            type=int,
            help='ID de una lección específica (opcional)'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Eliminar ejercicios duplicados antes de corregir'
        )

    def handle(self, *args, **options):
        leccion_id = options.get('leccion')
        limpiar = options.get('limpiar')

        if leccion_id:
            lecciones = Lesson.objects.filter(id=leccion_id, is_active=True)
        else:
            lecciones = Lesson.objects.filter(is_active=True)

        total_corregidos = 0
        total_creados = 0

        for lesson in lecciones:
            self.stdout.write(f'📚 Procesando: {lesson.title}')

            # Limpiar duplicados si se solicita
            if limpiar:
                eliminados = self.limpiar_duplicados(lesson)
                if eliminados > 0:
                    self.stdout.write(f'  🗑️ Eliminados {eliminados} duplicados')

            # Obtener ejercicios existentes
            ejercicios = lesson.exercises.all()
            total_existentes = ejercicios.count()

            if total_existentes < 6:
                # Crear ejercicios faltantes
                faltantes = 6 - total_existentes
                self.crear_ejercicios(lesson, faltantes)
                total_creados += faltantes
                self.stdout.write(f'  ✅ Creados {faltantes} nuevos ejercicios')

            # Corregir ejercicios existentes
            for ejercicio in ejercicios:
                if self.corregir_ejercicio(ejercicio):
                    total_corregidos += 1

            # Asegurar variedad de tipos
            self.variar_tipos(lesson)

            self.stdout.write(f'  📊 Total: {lesson.exercises.count()} ejercicios')
            self.stdout.write('')

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 RESULTADOS:'
            f'\n   Ejercicios corregidos: {total_corregidos}'
            f'\n   Ejercicios creados: {total_creados}'
        ))

    def limpiar_duplicados(self, lesson):
        """Elimina ejercicios duplicados"""
        preguntas_vistas = set()
        eliminados = 0

        for ejercicio in lesson.exercises.all():
            pregunta = ejercicio.question.strip()
            if pregunta in preguntas_vistas:
                ejercicio.delete()
                eliminados += 1
            else:
                preguntas_vistas.add(pregunta)

        return eliminados

    def corregir_ejercicio(self, ejercicio):
        """Corrige un ejercicio individual"""
        corregido = False

        # 1. Corregir opción correcta duplicada con las incorrectas
        if ejercicio.option_a == ejercicio.option_b or ejercicio.option_a == ejercicio.option_c:
            ejercicio.option_b = f"Definición alternativa {random.randint(1, 100)}"
            ejercicio.option_c = f"Definición errónea {random.randint(1, 100)}"
            corregido = True

        # 2. Asegurar que la opción correcta esté en A (si no, reordenar)
        if ejercicio.correct_answer != 'A' and ejercicio.correct_answer in ['B', 'C', 'D']:
            # Mover la correcta a A
            opciones = {
                'A': ejercicio.option_a,
                'B': ejercicio.option_b,
                'C': ejercicio.option_c,
                'D': ejercicio.option_d,
            }
            correcta = opciones.get(ejercicio.correct_answer, '')
            if correcta:
                ejercicio.option_a = correcta
                ejercicio.correct_answer = 'A'
                # Reubicar otras opciones
                opciones_nuevas = []
                for letra in ['A', 'B', 'C', 'D']:
                    if letra != ejercicio.correct_answer:
                        opciones_nuevas.append(opciones[letra])
                if len(opciones_nuevas) >= 3:
                    ejercicio.option_b = opciones_nuevas[0] if len(opciones_nuevas) > 0 else ''
                    ejercicio.option_c = opciones_nuevas[1] if len(opciones_nuevas) > 1 else ''
                    ejercicio.option_d = opciones_nuevas[2] if len(opciones_nuevas) > 2 else ''
                corregido = True

        # 3. Mejorar la pregunta (si es muy corta o genérica)
        if len(ejercicio.question) < 20:
            root = ejercicio.lesson.root if ejercicio.lesson.root else 'esta palabra'
            ejercicio.question = f"¿Cuál es el significado de '{root}'?"
            corregido = True

        # 4. Añadir explicación si no tiene
        if not ejercicio.explanation and ejercicio.option_a:
            significado = ejercicio.option_a[:100]
            ejercicio.explanation = f"La respuesta correcta es: {significado}"
            corregido = True

        if corregido:
            ejercicio.save()

        return corregido

    def crear_ejercicios(self, lesson, cantidad):
        """Crea ejercicios variados para una lección"""
        tipos = [
            self.crear_opcion_multiple,
            self.crear_verdadero_falso,
            self.crear_completar,
            self.crear_ordenar,
            self.crear_emparejar,
        ]

        root = lesson.root or 'palabra'
        meaning = lesson.meaning or 'significado'

        for i in range(cantidad):
            tipo = tipos[i % len(tipos)]
            ejercicio = tipo(lesson, root, meaning, i)
            if ejercicio:
                Exercise.objects.create(**ejercicio)

    def crear_opcion_multiple(self, lesson, root, meaning, idx):
        """Crea ejercicio de opción múltiple"""
        opciones = [
            meaning[:80] if meaning else 'Significado correcto',
            f"Definición incorrecta {idx+1}",
            f"Definición errónea {idx+1}",
            f"Definición alternativa {idx+1}"
        ]
        random.shuffle(opciones)
        opciones[0] = meaning[:80] if meaning else 'Significado correcto'

        return {
            'lesson': lesson,
            'exercise_type': 'multiple_choice',
            'question': f"¿Cuál es el significado de '{root[:50]}'?",
            'option_a': opciones[0][:200],
            'option_b': opciones[1][:200] if len(opciones) > 1 else '',
            'option_c': opciones[2][:200] if len(opciones) > 2 else '',
            'option_d': opciones[3][:200] if len(opciones) > 3 else '',
            'correct_answer': 'A',
            'explanation': f"La respuesta correcta es: {meaning[:100]}",
            'points': random.randint(1, 3),
            'is_active': True,
        }

    def crear_verdadero_falso(self, lesson, root, meaning, idx):
        """Crea ejercicio de Verdadero/Falso"""
        es_verdadero = random.choice([True, False])
        if es_verdadero:
            pregunta = f"La palabra '{root[:30]}' significa '{meaning[:30]}'."
            correcta = 'V'
            explicacion = f"Correcto. '{root[:30]}' significa '{meaning[:30]}'."
        else:
            falsos = ['casa', 'perro', 'tiempo', 'luz', 'oscuridad']
            falso = random.choice(falsos)
            pregunta = f"La palabra '{root[:30]}' significa '{falso}'."
            correcta = 'F'
            explicacion = f"Incorrecto. '{root[:30]}' significa '{meaning[:30]}', no '{falso}'."

        return {
            'lesson': lesson,
            'exercise_type': 'true_false',
            'question': pregunta,
            'option_a': 'Verdadero',
            'option_b': 'Falso',
            'option_c': '',
            'option_d': '',
            'correct_answer': correcta,
            'explanation': explicacion,
            'points': 1,
            'is_active': True,
        }

    def crear_completar(self, lesson, root, meaning, idx):
        """Crea ejercicio de completar"""
        palabras = (meaning or '').split()
        if len(palabras) > 3:
            pos = random.randint(1, len(palabras)-2)
            oculta = palabras[pos]
            palabras[pos] = '________'
            pregunta = f"Completa la definición de '{root[:30]}':\n{' '.join(palabras)}"

            return {
                'lesson': lesson,
                'exercise_type': 'fill_blank',
                'question': pregunta[:500],
                'option_a': oculta[:200],
                'option_b': f"Palabra incorrecta {idx+1}",
                'option_c': f"Palabra incorrecta {idx+2}",
                'option_d': f"Palabra incorrecta {idx+3}",
                'correct_answer': 'A',
                'explanation': f"La palabra correcta es '{oculta}'.",
                'points': 1,
                'is_active': True,
            }
        return None

    def crear_ordenar(self, lesson, root, meaning, idx):
        """Crea ejercicio de ordenar"""
        palabras = ['una', 'frase', 'de', 'ejemplo']
        random.shuffle(palabras)
        correcto = 'una frase de ejemplo'

        return {
            'lesson': lesson,
            'exercise_type': 'matching',
            'question': f"Ordena las palabras: {' '.join(palabras)}",
            'option_a': correcto[:200],
            'option_b': f"Orden incorrecto {idx+1}",
            'option_c': f"Orden incorrecto {idx+2}",
            'option_d': f"Orden incorrecto {idx+3}",
            'correct_answer': 'A',
            'explanation': f"El orden correcto es: {correcto}",
            'points': 1,
            'is_active': True,
        }

    def crear_emparejar(self, lesson, root, meaning, idx):
        """Crea ejercicio de emparejar"""
        return {
            'lesson': lesson,
            'exercise_type': 'matching',
            'question': f"Empareja '{root[:30]}' con su significado.",
            'option_a': meaning[:80] if meaning else 'Significado correcto',
            'option_b': f"Definición incorrecta {idx+1}",
            'option_c': f"Definición errónea {idx+1}",
            'option_d': f"Definición alternativa {idx+1}",
            'correct_answer': 'A',
            'explanation': f"'{root[:30]}' significa: {meaning[:100]}",
            'points': 1,
            'is_active': True,
        }

    def variar_tipos(self, lesson):
        """Asegura que haya variedad de tipos de ejercicios"""
        ejercicios = lesson.exercises.all()
        tipos = [e.exercise_type for e in ejercicios]

        # Si todos son del mismo tipo, convertir algunos
        if len(set(tipos)) == 1 and len(ejercicios) >= 3:
            for i, ejercicio in enumerate(ejercicios[:3]):
                if i == 0:
                    ejercicio.exercise_type = 'multiple_choice'
                elif i == 1:
                    ejercicio.exercise_type = 'true_false'
                elif i == 2:
                    ejercicio.exercise_type = 'fill_blank'
                ejercicio.save()

        # Si hay muchos de un tipo, balancear
        tipos_objetivo = ['multiple_choice', 'true_false', 'fill_blank', 'matching']
        for i, ejercicio in enumerate(ejercicios):
            if i < len(tipos_objetivo):
                ejercicio.exercise_type = tipos_objetivo[i % len(tipos_objetivo)]
                ejercicio.save()
