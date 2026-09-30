from django.core.management.base import BaseCommand
from core.models import Course, Lesson, Exercise
import random
import unicodedata
import re

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-zA-Z0-9]+', '-', text).lower().strip('-')

class Command(BaseCommand):
    help = 'Genera cursos con lecciones y ejercicios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cursos',
            type=int,
            default=45,
            help='Número de cursos a generar (por defecto 45)'
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
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Eliminar datos existentes antes de generar'
        )

    def handle(self, *args, **options):
        num_cursos = options['cursos']
        num_lecciones = options['lecciones']
        num_ejercicios = options['ejercicios']
        clean = options['clean']

        if clean:
            self.stdout.write('🧹 Eliminando datos existentes...')
            Exercise.objects.all().delete()
            Lesson.objects.all().delete()
            Course.objects.all().delete()
            self.stdout.write('✅ Datos eliminados')

        self.stdout.write(f'📚 Generando {num_cursos} cursos con {num_lecciones} lecciones y {num_ejercicios} ejercicios por lección...')

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
            "Literatura Realista", "Literatura de Aventuras", "Literatura de Viajes",
            "Literatura de Amor", "Literatura de Suspenso", "Literatura de Misterio",
            "Literatura de Guerra", "Literatura de Paz", "Literatura de la Naturaleza",
            "Literatura de la Ciudad", "Literatura del Campo", "Literatura del Mar",
            "Literatura del Cielo", "Literatura del Infierno", "Literatura del Paraíso",
            "Literatura de los Sueños", "Literatura de la Memoria", "Literatura del Olvido",
            "Literatura de la Esperanza", "Literatura del Dolor", "Literatura de la Alegría",
            "Literatura de la Locura", "Literatura de la Razón", "Literatura del Tiempo"
        ]

        while len(nombres_cursos) < num_cursos:
            nombres_cursos.append(f"Curso de Lengua {len(nombres_cursos)+1}")

        iconos = ['📚', '✍️', '🎯', '🧠', '📖', '🔍', '✏️', '📝', '🎓', '💡', '📜', '🔤', '🗣️', '📢', '🎤', '📕', '📗', '📘', '📙']

        total_cursos = 0
        total_lecciones = 0
        total_ejercicios = 0

        for i in range(num_cursos):
            nombre = nombres_cursos[i % len(nombres_cursos)]
            base_slug = slugify(nombre)
            # Slug único: nombre + número + random
            slug = f"{base_slug}-{i+1}-{random.randint(100,999)}"
            
            curso = Course.objects.create(
                slug=slug,
                name=nombre,
                description=f"Curso completo sobre {nombre.lower()} con {num_lecciones} lecciones prácticas.",
                icon=random.choice(iconos),
                category='general',
                is_active=True
            )
            total_cursos += 1

            for j in range(num_lecciones):
                raiz = f"{random.choice(['palabra','lengua','texto','discurso','sonido','escritura','lectura','comunicación','gramática','sintaxis'])}-{j+1}"
                significado = f"Concepto clave sobre {nombre.lower()} - Parte {j+1}"
                
                lesson = Lesson.objects.create(
                    course=curso,
                    order=j+1,
                    title=f"Lección {j+1}: {random.choice(['Fundamentos','Principios','Aplicaciones','Teoría','Práctica','Conceptos'])} de {nombre[:20]}",
                    root=raiz,
                    meaning=significado,
                    example=f"Ejemplo práctico de {nombre.lower()} en contexto.",
                    breakdown=f"{raiz} + {random.choice(['-ción', '-miento', '-aje', '-dad'])} → {random.choice(['acción', 'proceso', 'resultado'])}",
                    difficulty=random.choice(['beginner', 'intermediate', 'advanced']),
                    duration_minutes=random.randint(3, 15),
                    is_active=True
                )
                total_lecciones += 1

                for k in range(num_ejercicios):
                    opciones = [
                        significado[:50],
                        f"Definición incorrecta {k+1}",
                        f"Definición errónea {k+1}",
                        f"Otro significado {k+1}"
                    ]
                    random.shuffle(opciones)
                    opciones[0] = significado[:50]

                    Exercise.objects.create(
                        lesson=lesson,
                        exercise_type='multiple_choice',
                        question=f"¿Cuál es el significado de '{raiz}'?",
                        option_a=opciones[0][:200],
                        option_b=opciones[1][:200] if len(opciones) > 1 else '',
                        option_c=opciones[2][:200] if len(opciones) > 2 else '',
                        option_d=opciones[3][:200] if len(opciones) > 3 else '',
                        correct_answer='A',
                        explanation=f"La respuesta correcta es: {significado[:200]}",
                        points=random.randint(1, 3),
                        is_active=True
                    )
                    total_ejercicios += 1

            if (i + 1) % 10 == 0:
                self.stdout.write(f'📊 Progreso: {i+1}/{num_cursos} cursos creados')

        self.stdout.write(self.style.SUCCESS(f'\n🎉 RESULTADOS FINALES:'))
        self.stdout.write(f'   Cursos creados: {total_cursos}')
        self.stdout.write(f'   Lecciones creadas: {total_lecciones}')
        self.stdout.write(f'   Ejercicios creados: {total_ejercicios}')
