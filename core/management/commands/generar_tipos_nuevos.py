"""
🎯 GENERADOR DE 5 TIPOS NUEVOS DE PREGUNTAS
============================================
- Corrige los 5 tipos de preguntas existentes
- Añade 5 nuevos tipos de ejercicios interactivos
- Mejora la experiencia de aprendizaje
"""

from django.core.management.base import BaseCommand
from core.models import Lesson, Exercise
import random

class Command(BaseCommand):
    help = 'Genera 5 nuevos tipos de ejercicios interactivos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--leccion',
            type=int,
            help='ID de una lección específica (opcional)'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Eliminar ejercicios antiguos y crear nuevos'
        )
        parser.add_argument(
            '--cantidad',
            type=int,
            default=10,
            help='Número de ejercicios por lección (por defecto 10)'
        )

    def handle(self, *args, **options):
        leccion_id = options.get('leccion')
        limpiar = options.get('limpiar')
        cantidad = options.get('cantidad', 10)

        if leccion_id:
            lecciones = Lesson.objects.filter(id=leccion_id, is_active=True)
        else:
            lecciones = Lesson.objects.filter(is_active=True)

        total_creados = 0

        for lesson in lecciones:
            self.stdout.write(f'📚 Procesando: {lesson.title}')

            # Limpiar ejercicios antiguos si se solicita
            if limpiar:
                count = lesson.exercises.count()
                lesson.exercises.all().delete()
                self.stdout.write(f'  🗑️ Eliminados {count} ejercicios antiguos')

            # Obtener datos de la lección
            root = lesson.root or 'palabra'
            meaning = lesson.meaning or 'significado'
            example = lesson.example or 'ejemplo'
            breakdown = lesson.breakdown or 'desglose'

            # Generar ejercicios con los 10 tipos
            creados = self.generar_ejercicios_mixtos(lesson, root, meaning, example, breakdown, cantidad)
            total_creados += creados

            self.stdout.write(f'  ✅ Creados {creados} ejercicios (10 tipos variados)')

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 RESULTADOS:'
            f'\n   Total ejercicios creados: {total_creados}'
            f'\n   Tipos disponibles: 10 (5 existentes + 5 nuevos)'
        ))

    def generar_ejercicios_mixtos(self, lesson, root, meaning, example, breakdown, cantidad):
        """Genera ejercicios combinando 5 tipos existentes y 5 nuevos"""
        creados = 0
        tipos_creados = 0

        # Lista de funciones generadoras
        generadores = [
            self.opcion_multiple_mejorado,
            self.verdadero_falso_mejorado,
            self.completar_mejorado,
            self.ordenar_mejorado,
            self.emparejar_mejorado,
            self.seleccion_multiple,
            self.arrastrar_soltar,
            self.clasificacion,
            self.pregunta_abierta,
            self.asociacion_imagen,
        ]

        # Generar hasta la cantidad deseada
        for i in range(cantidad):
            generador = generadores[i % len(generadores)]
            ejercicio = generador(lesson, root, meaning, example, breakdown, i)
            if ejercicio:
                Exercise.objects.create(**ejercicio)
                creados += 1
                tipos_creados += 1

        return creados

    # ============================================================
    # 5 TIPOS EXISTENTES (MEJORADOS)
    # ============================================================

    def opcion_multiple_mejorado(self, lesson, root, meaning, example, breakdown, idx):
        """Opción múltiple mejorada con opciones más variadas"""
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
            'question': f"📝 ¿Cuál es el significado de '{root[:50]}'?",
            'option_a': opciones[0][:200],
            'option_b': opciones[1][:200] if len(opciones) > 1 else '',
            'option_c': opciones[2][:200] if len(opciones) > 2 else '',
            'option_d': opciones[3][:200] if len(opciones) > 3 else '',
            'correct_answer': 'A',
            'explanation': f"✅ La respuesta correcta es: {meaning[:100]}",
            'points': random.randint(1, 3),
            'is_active': True,
        }

    def verdadero_falso_mejorado(self, lesson, root, meaning, example, breakdown, idx):
        """Verdadero/Falso con contexto más rico"""
        es_verdadero = random.choice([True, False])
        if es_verdadero:
            pregunta = f"⚖️ ¿La raíz '{root[:30]}' significa '{meaning[:30]}'?"
            correcta = 'V'
            explicacion = f"✅ Correcto. '{root[:30]}' significa '{meaning[:30]}'."
        else:
            falsos = ['casa', 'perro', 'tiempo', 'luz', 'oscuridad', 'cielo', 'mar', 'flor']
            falso = random.choice(falsos)
            pregunta = f"⚖️ ¿La raíz '{root[:30]}' significa '{falso}'?"
            correcta = 'F'
            explicacion = f"❌ Incorrecto. '{root[:30]}' significa '{meaning[:30]}', no '{falso}'."

        return {
            'lesson': lesson,
            'exercise_type': 'true_false',
            'question': pregunta,
            'option_a': '✅ Verdadero',
            'option_b': '❌ Falso',
            'option_c': '',
            'option_d': '',
            'correct_answer': correcta,
            'explanation': explicacion,
            'points': 1,
            'is_active': True,
        }

    def completar_mejorado(self, lesson, root, meaning, example, breakdown, idx):
        """Completar con más contexto"""
        palabras = (meaning or '').split()
        if len(palabras) > 3:
            pos = random.randint(1, len(palabras)-2)
            oculta = palabras[pos]
            palabras[pos] = '________'
            pregunta = f"📝 Completa la definición de '{root[:30]}':\n{' '.join(palabras)}"

            return {
                'lesson': lesson,
                'exercise_type': 'fill_blank',
                'question': pregunta[:500],
                'option_a': oculta[:200],
                'option_b': f"Palabra incorrecta {idx+1}",
                'option_c': f"Palabra incorrecta {idx+2}",
                'option_d': f"Palabra incorrecta {idx+3}",
                'correct_answer': 'A',
                'explanation': f"✅ La palabra correcta es '{oculta}'.",
                'points': 1,
                'is_active': True,
            }
        return None

    def ordenar_mejorado(self, lesson, root, meaning, example, breakdown, idx):
        """Ordenar con más variedad"""
        frases = [
            ['una', 'frase', 'de', 'ejemplo'],
            ['el', 'perro', 'corre', 'rápido'],
            ['la', 'casa', 'es', 'grande'],
            ['los', 'estudiantes', 'estudian', 'mucho'],
            ['ella', 'canta', 'bien', 'siempre'],
        ]
        palabras = random.choice(frases)
        random.shuffle(palabras)
        correcto = ' '.join(random.choice(frases))

        return {
            'lesson': lesson,
            'exercise_type': 'matching',
            'question': f"🔄 Ordena correctamente: {' '.join(palabras)}",
            'option_a': correcto[:200],
            'option_b': f"Orden incorrecto {idx+1}",
            'option_c': f"Orden incorrecto {idx+2}",
            'option_d': f"Orden incorrecto {idx+3}",
            'correct_answer': 'A',
            'explanation': f"✅ El orden correcto es: {correcto}",
            'points': 1,
            'is_active': True,
        }

    def emparejar_mejorado(self, lesson, root, meaning, example, breakdown, idx):
        """Emparejar con más opciones"""
        return {
            'lesson': lesson,
            'exercise_type': 'matching',
            'question': f"🔗 Empareja '{root[:30]}' con su significado.",
            'option_a': meaning[:80] if meaning else 'Significado correcto',
            'option_b': f"Definición incorrecta {idx+1}",
            'option_c': f"Definición errónea {idx+1}",
            'option_d': f"Definición alternativa {idx+1}",
            'correct_answer': 'A',
            'explanation': f"✅ '{root[:30]}' significa: {meaning[:100]}",
            'points': 1,
            'is_active': True,
        }

    # ============================================================
    # 5 NUEVOS TIPOS DE PREGUNTAS
    # ============================================================

    def seleccion_multiple(self, lesson, root, meaning, example, breakdown, idx):
        """TIPO 6: Selección Múltiple (elige varias opciones correctas)"""
        correctas = []
        palabras = (meaning or '').split()
        if len(palabras) >= 2:
            correctas = [meaning[:60], f"{palabras[0]} {palabras[-1]}" if len(palabras) > 1 else meaning[:40]]
        else:
            correctas = [meaning[:60], f"{meaning[:30]} correcto"]

        while len(correctas) < 2:
            correctas.append(f"Significado correcto {len(correctas)+1}")

        incorrectas = [f"Definición incorrecta {idx+1}", f"Definición errónea {idx+1}"]

        opciones = correctas + incorrectas
        random.shuffle(opciones)

        correctas_pos = [i for i, opt in enumerate(opciones) if opt in correctas]

        return {
            'lesson': lesson,
            'exercise_type': 'multiple_choice',
            'question': f"🎯 Selecciona TODAS las definiciones correctas para '{root[:30]}' (elige 2):",
            'option_a': opciones[0][:200] if len(opciones) > 0 else '',
            'option_b': opciones[1][:200] if len(opciones) > 1 else '',
            'option_c': opciones[2][:200] if len(opciones) > 2 else '',
            'option_d': opciones[3][:200] if len(opciones) > 3 else '',
            'correct_answer': ''.join(['A', 'B', 'C', 'D'][i] for i in correctas_pos[:2]),
            'explanation': f"✅ Las respuestas correctas son: {correctas[0][:60]} y {correctas[1][:60]}",
            'points': 2,
            'is_active': True,
        }

    def arrastrar_soltar(self, lesson, root, meaning, example, breakdown, idx):
        """TIPO 7: Arrastrar y Soltar (ordenar conceptos)"""
        secuencia = [
            root[:30],
            meaning[:30] if meaning else 'concepto',
            example[:30] if example else 'ejemplo',
            breakdown[:30] if breakdown else 'desglose'
        ]
        random.shuffle(secuencia)
        correcto = f"{root[:30]} → {meaning[:30] if meaning else 'concepto'}"

        return {
            'lesson': lesson,
            'exercise_type': 'matching',
            'question': f"🖱️ Arrastra y ordena los conceptos:\n{' | '.join(secuencia)}",
            'option_a': correcto[:200],
            'option_b': f"Orden incorrecto {idx+1}",
            'option_c': f"Orden incorrecto {idx+2}",
            'option_d': f"Orden incorrecto {idx+3}",
            'correct_answer': 'A',
            'explanation': f"✅ El orden correcto es: {correcto}",
            'points': 2,
            'is_active': True,
        }

    def clasificacion(self, lesson, root, meaning, example, breakdown, idx):
        """TIPO 8: Clasificación (categorizar palabras)"""
        categorias = [
            {'nombre': 'Sustantivos', 'ejemplos': ['casa', 'perro', 'libro', 'mesa']},
            {'nombre': 'Adjetivos', 'ejemplos': ['grande', 'pequeño', 'rojo', 'feliz']},
            {'nombre': 'Verbos', 'ejemplos': ['correr', 'saltar', 'comer', 'dormir']},
            {'nombre': 'Adverbios', 'ejemplos': ['bien', 'mal', 'rápido', 'lento']},
        ]
        cat = random.choice(categorias)

        return {
            'lesson': lesson,
            'exercise_type': 'multiple_choice',
            'question': f"📂 ¿Cuál de estas palabras es un {cat['nombre']}?\n{', '.join(cat['ejemplos'])}",
            'option_a': cat['ejemplos'][0][:200],
            'option_b': cat['ejemplos'][1][:200],
            'option_c': cat['ejemplos'][2][:200],
            'option_d': cat['ejemplos'][3][:200],
            'correct_answer': 'A',
            'explanation': f"✅ {cat['ejemplos'][0]} es un {cat['nombre']}.",
            'points': 2,
            'is_active': True,
        }

    def pregunta_abierta(self, lesson, root, meaning, example, breakdown, idx):
        """TIPO 9: Pregunta Abierta con opciones sugeridas"""
        return {
            'lesson': lesson,
            'exercise_type': 'fill_blank',
            'question': f"✍️ Describe el significado de '{root[:30]}' y da un ejemplo.",
            'option_a': f"Significado: {meaning[:80] if meaning else 'Definición correcta'}",
            'option_b': f"Ejemplo: {example[:50] if example else 'Una frase con la palabra'}",
            'option_c': f"Sinónimo: {random.choice(['palabra similar', 'término relacionado'])}",
            'option_d': f"Antónimo: {random.choice(['palabra opuesta', 'término contrario'])}",
            'correct_answer': 'A',
            'explanation': f"✅ El significado correcto es: {meaning[:100]}\nEjemplo: {root[:30]} se usa para...",
            'points': 3,
            'is_active': True,
        }

    def asociacion_imagen(self, lesson, root, meaning, example, breakdown, idx):
        """TIPO 10: Asociación de Imágenes (concepto-imagen descrita)"""
        imagenes = [
            {'nombre': '🌳 árbol', 'descripcion': 'planta grande con tronco'},
            {'nombre': '🐱 gato', 'descripcion': 'animal doméstico felino'},
            {'nombre': '📚 libro', 'descripcion': 'conjunto de páginas escritas'},
            {'nombre': '🏠 casa', 'descripcion': 'lugar donde se vive'},
        ]
        img = random.choice(imagenes)

        return {
            'lesson': lesson,
            'exercise_type': 'multiple_choice',
            'question': f"🖼️ Asocia la imagen con su concepto:\n{img['nombre']}\n{img['descripcion']}",
            'option_a': f"{img['nombre']} - {img['descripcion']}",
            'option_b': f"Imagen incorrecta {idx+1}",
            'option_c': f"Imagen incorrecta {idx+2}",
            'option_d': f"Imagen incorrecta {idx+3}",
            'correct_answer': 'A',
            'explanation': f"✅ {img['nombre']} es {img['descripcion']}.",
            'points': 2,
            'is_active': True,
        }
