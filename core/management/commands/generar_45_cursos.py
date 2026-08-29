from django.core.management.base import BaseCommand
from core.models import Course, Lesson, Exercise
import random
import unicodedata
import re

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-zA-Z0-9]+', '-', text).lower().strip('-')

class Command(BaseCommand):
    help = 'Genera 45 cursos con lecciones y ejercicios para el dashboard del profesor'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Eliminar todos los cursos, lecciones y ejercicios existentes antes de generar'
        )
        parser.add_argument(
            '--lecciones',
            type=int,
            default=10,
            help='Número de lecciones por curso (por defecto 10)'
        )
        parser.add_argument(
            '--ejercicios',
            type=int,
            default=5,
            help='Número de ejercicios por lección (por defecto 5)'
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('🧹 Eliminando datos existentes...')
            Exercise.objects.all().delete()
            Lesson.objects.all().delete()
            Course.objects.all().delete()
            self.stdout.write('✅ Datos eliminados')

        self.stdout.write(f'📚 Generando 45 cursos con {options["lecciones"]} lecciones y {options["ejercicios"]} ejercicios por lección...')

        # Lista de nombres de cursos reales y variados
        nombres_cursos = [
            "Ortografía Avanzada", "Gramática del Castellano", "Figuras Retóricas",
            "Sintaxis Básica", "Semántica y Pragmática", "Fonética y Fonología",
            "Redacción Científica", "Periodismo y Crónica", "Literatura Hispanoamericana",
            "Poesía Castellana", "Análisis del Discurso", "Comunicación Efectiva",
            "Escritura Académica", "Argumentación Jurídica", "Narrativa Creativa",
            "Descripción y Detalle", "Exposición de Ideas", "Comparación y Contraste",
            "Conectores y Cohesión", "Signos de Puntuación", "Morfología del Castellano",
            "Etimología Grecolatina", "Lexicografía Española", "Dialectología Hispánica",
            "Sociolingüística", "Psicolingüística", "Neurolingüística",
            "Lingüística Cognitiva", "Lingüística Computacional", "Lingüística Histórica",
            "Filosofía del Lenguaje", "Retórica Clásica", "Retórica Moderna",
            "Estilística", "Crítica Literaria", "Teoría Literaria",
            "Literatura Infantil", "Literatura Juvenil", "Literatura Fantástica",
            "Literatura de Ciencia Ficción", "Literatura de Terror", "Literatura Romántica",
            "Literatura Realista", "Literatura de Aventuras", "Literatura de Viajes"
        ]

        # Asegurar que tenemos al menos 45 nombres
        while len(nombres_cursos) < 45:
            nombres_cursos.append(f"Curso de Lengua {len(nombres_cursos)+1}")

        # Tipos de ejercicios
        tipos_ejercicio = ['multiple_choice', 'true_false', 'fill_blank', 'matching', 'multiple_choice']

        # Iconos aleatorios
        iconos = ['📚', '✍️', '🎯', '🧠', '📖', '🔍', '✏️', '📝', '🎓', '💡', '📜', '🔤', '🗣️', '📢', '🎤']

        total_cursos = 0
        total_lecciones = 0
        total_ejercicios = 0

        for i in range(45):
            nombre = nombres_cursos[i]
            slug = slugify(nombre)
            icono = random.choice(iconos)

            curso = Course.objects.create(
                slug=slug,
                name=nombre,
                description=f"Curso completo sobre {nombre.lower()} con {options['lecciones']} lecciones prácticas.",
                icon=icono,
                category='general',
                is_active=True
            )
            total_cursos += 1

            # Generar lecciones
            for j in range(options['lecciones']):
                # Lecciones con contenido variado
                raices = ['palabra', 'lengua', 'texto', 'discurso', 'sonido', 'escritura', 'lectura', 'comunicación']
                raiz = f"{random.choice(raices)}-{j+1}"
                significado = f"Concepto clave sobre {nombre.lower()} - Parte {j+1}"
                ejemplo = f"Ejemplo práctico de {nombre.lower()} en contexto."

                lesson = Lesson.objects.create(
                    course=curso,
                    order=j+1,
                    title=f"Lección {j+1}: {random.choice(['Fundamentos', 'Principios', 'Aplicaciones', 'Casos', 'Teoría', 'Práctica'])} de {nombre}",
                    root=raiz,
                    meaning=significado,
                    example=ejemplo,
                    breakdown=f"{raiz} + {random.choice(['-ción', '-miento', '-aje', '-dad'])} → {random.choice(['acción', 'proceso', 'resultado'])}",
                    difficulty=random.choice(['beginner', 'intermediate', 'advanced']),
                    duration_minutes=random.randint(3, 15),
                    is_active=True
                )
                total_lecciones += 1

                # Generar ejercicios
                for k in range(options['ejercicios']):
                    tipo = random.choice(tipos_ejercicio)
                    if tipo == 'multiple_choice':
                        pregunta = f"¿Cuál es el significado de '{raiz}'?"
                        opciones = [
                            significado[:50],
                            f"Definición incorrecta {k+1}",
                            f"Definición errónea {k+1}",
                            f"Otro significado {k+1}"
                        ]
                        random.shuffle(opciones)
                        correcta = 'A'
                        # Aseguramos que la correcta esté en A
                        opciones[0] = significado[:50]
                        explanation = f"La respuesta correcta es: {significado[:100]}"
                    elif tipo == 'true_false':
                        verdadero = random.choice([True, False])
                        if verdadero:
                            pregunta = f"'{raiz}' significa '{significado[:30]}'."
                            correcta = 'V'
                            explanation = "Correcto, esa es la definición."
                        else:
                            pregunta = f"'{raiz}' significa '{random.choice(['casa', 'perro', 'luz', 'oscuridad'])}'."
                            correcta = 'F'
                            explanation = f"Incorrecto, '{raiz}' significa '{significado[:30]}'."
                    elif tipo == 'fill_blank':
                        palabras = significado.split()
                        if len(palabras) > 2:
                            idx = random.randint(1, len(palabras)-2)
                            oculta = palabras[idx]
                            palabras[idx] = '________'
                            pregunta = f"Completa la definición de '{raiz}':\n{' '.join(palabras)}"
                            correcta = 'A'
                            opciones = [oculta, f"Palabra {k+1}", f"Palabra {k+2}", f"Palabra {k+3}"]
                            random.shuffle(opciones)
                            # Aseguramos que la correcta esté en A
                            opciones[0] = oculta
                            explanation = f"La palabra correcta es '{oculta}'."
                        else:
                            # Si no se puede, usar opción múltiple simple
                            tipo = 'multiple_choice'
                            pregunta = f"¿Cuál es el significado de '{raiz}'?"
                            opciones = [significado[:50], f"Definición incorrecta {k+1}", f"Definición errónea {k+1}", f"Otro significado {k+1}"]
                            random.shuffle(opciones)
                            opciones[0] = significado[:50]
                            correcta = 'A'
                            explanation = f"La respuesta correcta es: {significado[:100]}"
                    elif tipo == 'matching':
                        pregunta = f"Empareja '{raiz}' con su significado."
                        opciones = [significado[:50], f"Definición incorrecta {k+1}", f"Definición errónea {k+1}", f"Definición incorrecta {k+2}"]
                        random.shuffle(opciones)
                        opciones[0] = significado[:50]
                        correcta = 'A'
                        explanation = f"'{raiz}' significa: {significado[:100]}"
                    else:
                        # Por defecto opción múltiple
                        pregunta = f"¿Cuál es el significado de '{raiz}'?"
                        opciones = [significado[:50], f"Definición incorrecta {k+1}", f"Definición errónea {k+1}", f"Otro significado {k+1}"]
                        random.shuffle(opciones)
                        opciones[0] = significado[:50]
                        correcta = 'A'
                        explanation = f"La respuesta correcta es: {significado[:100]}"

                    # Crear el ejercicio
                    Exercise.objects.create(
                        lesson=lesson,
                        exercise_type=tipo,
                        question=pregunta[:500],
                        option_a=opciones[0][:200],
                        option_b=opciones[1][:200] if len(opciones) > 1 else '',
                        option_c=opciones[2][:200] if len(opciones) > 2 else '',
                        option_d=opciones[3][:200] if len(opciones) > 3 else '',
                        correct_answer=correcta,
                        explanation=explanation[:500],
                        points=random.randint(1, 3),
                        is_active=True
                    )
                    total_ejercicios += 1

            self.stdout.write(f'✅ Curso {i+1}: {nombre}')

        self.stdout.write(self.style.SUCCESS(f'\n🎉 RESULTADOS:'))
        self.stdout.write(f'   Cursos creados: {total_cursos}')
        self.stdout.write(f'   Lecciones creadas: {total_lecciones}')
        self.stdout.write(f'   Ejercicios creados: {total_ejercicios}')
