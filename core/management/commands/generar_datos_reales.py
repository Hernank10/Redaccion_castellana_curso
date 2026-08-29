"""
Generador automático de datos con contenido REAL.
Crea cursos con lecciones basadas en listas temáticas auténticas.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Course, Lesson, Exercise, UserProgress, UserScore, UserStreak
import random
import unicodedata
import re

def slugify(text):
    """Convierte texto a slug válido para URLs"""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-zA-Z0-9]+', '-', text).lower().strip('-')

class Command(BaseCommand):
    help = 'Genera datos de prueba con contenido real y significativo'

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

        self.stdout.write('📚 Generando contenido REAL...')

        # Contenido real por temática
        contenido = {
            'Ortografía Avanzada': [
                ('Uso de la b', 'Se escribe b antes de consonante', 'blanco, brazo, abrir', 'Regla ortográfica'),
                ('Uso de la v', 'Se escribe v después de n', 'envase, invierno, enviar', 'Regla ortográfica'),
                ('Palabras agudas', 'Llevan tilde al final en vocal, n o s', 'camión, corazón, reloj', 'Acentuación'),
                ('Palabras graves', 'Llevan tilde si NO terminan en vocal, n o s', 'árbol, lápiz, fácil', 'Acentuación'),
                ('Palabras esdrújulas', 'Siempre llevan tilde', 'pájaro, médico, teléfono', 'Acentuación'),
                ('Uso de la h', 'Se escribe h en palabras que comienzan con hue-', 'hueso, huerta, huevo', 'Regla ortográfica'),
                ('Uso de la g', 'Se escribe g ante e, i', 'gente, general, gitano', 'Regla ortográfica'),
                ('Uso de la j', 'Se escribe j en verbos terminados en -jer', 'tejer, crujir, proteger', 'Regla ortográfica'),
                ('Uso de la c', 'Se escribe c ante e, i', 'cebra, cien, cocer', 'Regla ortográfica'),
                ('Uso de la z', 'Se escribe z ante a, o, u', 'zapato, zorro, zumo', 'Regla ortográfica'),
                ('Uso de la ll', 'Se escribe ll en palabras que comienzan con cha-', 'llave, calle, caballo', 'Regla ortográfica'),
                ('Uso de la y', 'Se escribe y en palabras que terminan en -y', 'rey, ley, hoy', 'Regla ortográfica'),
                ('Tilde diacrítica', 'Distingue palabras de igual forma', 'té (bebida) vs te (pronombre)', 'Acentuación'),
                ('Uso de la r', 'Se escribe r al inicio de palabra', 'rojo, ratón, rosa', 'Regla ortográfica'),
                ('Uso de la rr', 'Se escribe rr entre vocales', 'carro, perro, tierra', 'Regla ortográfica'),
                ('Uso de la x', 'Se escribe x en palabras que comienzan con ex-', 'excelente, exacto, exquisito', 'Regla ortográfica'),
                ('Mayúsculas', 'Se usan al inicio de oración y nombres propios', 'Juan, Colombia, El Quijote', 'Norma ortográfica'),
                ('Minúsculas', 'Se usan en el resto de casos', 'casa, libro, mesa', 'Norma ortográfica'),
                ('Uso del punto', 'Marca el final de una oración', 'Llegué tarde. Perdí el autobús.', 'Signo de puntuación'),
                ('Uso de la coma', 'Separa elementos en una enumeración', 'Compré pan, leche, huevos', 'Signo de puntuación'),
            ],
            'Gramática del Castellano': [
                ('El sustantivo', 'Nombra personas, animales, cosas o ideas', 'Juan, perro, casa, felicidad', 'Categoría gramatical'),
                ('El adjetivo', 'Acompaña al sustantivo y expresa cualidades', 'grande, pequeño, rojo, feliz', 'Categoría gramatical'),
                ('El verbo', 'Expresa acción, estado o proceso', 'correr, ser, estar, pensar', 'Categoría gramatical'),
                ('El adverbio', 'Modifica al verbo, adjetivo u otro adverbio', 'bien, mal, aquí, allí', 'Categoría gramatical'),
                ('La preposición', 'Relaciona elementos de la oración', 'a, de, en, para, por', 'Categoría gramatical'),
                ('La conjunción', 'Une oraciones o elementos', 'y, o, pero, aunque', 'Categoría gramatical'),
                ('El artículo', 'Acompaña al sustantivo', 'el, la, los, las, un, una', 'Categoría gramatical'),
                ('El pronombre', 'Sustituye al sustantivo', 'yo, tú, él, ella, nosotros', 'Categoría gramatical'),
                ('Concordancia nominal', 'Relación de género y número', 'casa bonita (femenino singular)', 'Concordancia'),
                ('Concordancia verbal', 'Relación de número y persona', 'Yo estudio, ellos estudian', 'Concordancia'),
                ('Oración simple', 'Un solo verbo conjugado', 'Juan estudia en la biblioteca', 'Sintaxis'),
                ('Oración compuesta', 'Más de un verbo conjugado', 'Juan estudia y María trabaja', 'Sintaxis'),
                ('Sujeto', 'Quién realiza la acción', 'Juan estudia', 'Elemento de la oración'),
                ('Predicado', 'Lo que se dice del sujeto', 'estudia en la biblioteca', 'Elemento de la oración'),
                ('Complemento directo', 'Recibe la acción del verbo', 'Compré un libro', 'Complemento verbal'),
                ('Complemento indirecto', 'Destinatario de la acción', 'Di el regalo a María', 'Complemento verbal'),
                ('Complemento circunstancial', 'Expresa circunstancias', 'Llegó ayer', 'Complemento verbal'),
                ('Verbos regulares', 'Siguen un patrón de conjugación', 'amar, temer, partir', 'Conjugación'),
                ('Verbos irregulares', 'No siguen un patrón', 'ser, estar, ir, haber', 'Conjugación'),
                ('Modos verbales', 'Indicativo, subjuntivo, imperativo', 'hablo, hable, habla', 'Modos'),
            ],
            'Figuras Retóricas': [
                ('Metáfora', 'Comparación implícita entre dos términos', 'El tiempo es oro', 'Figura retórica'),
                ('Símil', 'Comparación explícita con "como"', 'Brillaba como el sol', 'Figura retórica'),
                ('Hipérbole', 'Exageración intencionada', 'Pesaba una tonelada', 'Figura retórica'),
                ('Ironía', 'Decir lo contrario de lo que se piensa', '¡Qué buen día! (lloviendo)', 'Figura retórica'),
                ('Antítesis', 'Contraposición de ideas contrarias', 'Eres la luz y la sombra', 'Figura retórica'),
                ('Paradoja', 'Contradicción aparente', 'Vivo sin vivir en mí', 'Figura retórica'),
                ('Personificación', 'Atribuir cualidades humanas', 'El viento susurraba', 'Figura retórica'),
                ('Aliteración', 'Repetición de sonidos', 'El susurro de la seda', 'Figura retórica'),
                ('Anáfora', 'Repetición al inicio de versos', 'Corre el río, corre el viento', 'Figura retórica'),
                ('Epífora', 'Repetición al final de versos', 'Todo lo que necesitas es amor, todo lo que quieres es amor', 'Figura retórica'),
                ('Polisíndeton', 'Uso excesivo de conjunciones', 'Y corre y salta y ríe', 'Figura retórica'),
                ('Asíndeton', 'Omisión de conjunciones', 'Vine, vi, vencí', 'Figura retórica'),
                ('Hipérbaton', 'Alteración del orden lógico', 'Al campo me voy', 'Figura retórica'),
                ('Oxímoron', 'Unión de términos contradictorios', 'Un silencio ensordecedor', 'Figura retórica'),
                ('Sinécdoque', 'Parte por el todo o viceversa', 'Tiene veinte primaveras', 'Figura retórica'),
                ('Metonimia', 'Sustitución por relación de contigüidad', 'La corona habló al pueblo', 'Figura retórica'),
                ('Eufemismo', 'Sustitución de término desagradable', 'Pasar a mejor vida', 'Figura retórica'),
                ('Prosopopeya', 'Personificación de objetos abstractos', 'La esperanza sonríe', 'Figura retórica'),
                ('Apóstrofe', 'Interpelación a alguien o algo', '¡Oh, muerte!', 'Figura retórica'),
                ('Gradación', 'Orden ascendente o descendente', 'Llegó, vio y venció', 'Figura retórica'),
            ],
            'Fonética y Fonología': [
                ('Vocal [a]', 'Vocal central baja abierta', 'casa [ˈkasa]', 'Vocal'),
                ('Vocal [e]', 'Vocal media anterior', 'peso [ˈpeso]', 'Vocal'),
                ('Vocal [i]', 'Vocal alta anterior', 'vino [ˈbino]', 'Vocal'),
                ('Vocal [o]', 'Vocal media posterior', 'boca [ˈboka]', 'Vocal'),
                ('Vocal [u]', 'Vocal alta posterior', 'luna [ˈluna]', 'Vocal'),
                ('Consonante [p]', 'Oclusiva bilabial sorda', 'papa [ˈpapa]', 'Consonante'),
                ('Consonante [b]', 'Oclusiva bilabial sonora', 'baba [ˈbaba]', 'Consonante'),
                ('Consonante [t]', 'Oclusiva dental sorda', 'tata [ˈtata]', 'Consonante'),
                ('Consonante [d]', 'Oclusiva dental sonora', 'dado [ˈdado]', 'Consonante'),
                ('Consonante [k]', 'Oclusiva velar sorda', 'casa [ˈkasa]', 'Consonante'),
                ('Consonante [g]', 'Oclusiva velar sonora', 'gato [ˈgato]', 'Consonante'),
                ('Consonante [f]', 'Fricativa labiodental sorda', 'faro [ˈfaɾo]', 'Consonante'),
                ('Consonante [s]', 'Fricativa alveolar sorda', 'sapo [ˈsapo]', 'Consonante'),
                ('Consonante [x]', 'Fricativa velar sorda', 'jota [ˈxota]', 'Consonante'),
                ('Consonante [m]', 'Nasal bilabial', 'mamá [maˈma]', 'Consonante'),
                ('Consonante [n]', 'Nasal alveolar', 'nana [ˈnana]', 'Consonante'),
                ('Consonante [ɲ]', 'Nasal palatal (ñ)', 'niño [ˈniɲo]', 'Consonante'),
                ('Consonante [l]', 'Lateral alveolar', 'lala [ˈlala]', 'Consonante'),
                ('Consonante [r]', 'Vibrante múltiple', 'carro [ˈkaro]', 'Consonante'),
                ('Consonante [ɾ]', 'Vibrante simple', 'caro [ˈkaɾo]', 'Consonante'),
            ],
        }

        total_cursos = 0
        for nombre, lecciones_data in contenido.items():
            slug = slugify(nombre)
            course, created = Course.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': nombre,
                    'description': f"Curso completo sobre {nombre.lower()} con {len(lecciones_data)} lecciones prácticas.",
                    'icon': random.choice(['📚', '✍️', '🎯', '🧠', '📖', '🔍', '✏️', '📝', '🎓', '💡']),
                    'category': 'general',
                    'is_active': True
                }
            )
            if created:
                total_cursos += 1

            # Si el curso ya existe, eliminar sus lecciones para regenerarlas
            if not created:
                course.lessons.all().delete()

            # Crear lecciones
            for i, (root, meaning, example, breakdown) in enumerate(lecciones_data, 1):
                lesson = Lesson.objects.create(
                    course=course,
                    order=i,
                    title=f"{root[:50]}",
                    root=root[:100],
                    meaning=meaning[:300],
                    example=example[:300] if example else '',
                    breakdown=breakdown[:300] if breakdown else '',
                    difficulty=random.choice(['beginner', 'intermediate', 'advanced']),
                    duration_minutes=random.randint(3, 15),
                    is_active=True
                )

                # Crear 2 ejercicios por lección
                for j in range(2):
                    Exercise.objects.create(
                        lesson=lesson,
                        exercise_type='multiple_choice',
                        question=f"¿Cuál es el significado de '{root}'?",
                        option_a=f"{meaning[:50]}",
                        option_b=f"Significado incorrecto 1",
                        option_c=f"Significado incorrecto 2",
                        option_d=f"Significado incorrecto 3",
                        correct_answer='A',
                        explanation=f"La respuesta correcta es: {meaning[:100]}",
                        points=1
                    )

            self.stdout.write(f'✅ Curso: {course.name} - {course.lessons.count()} lecciones')

        # Crear usuarios de prueba
        if not User.objects.filter(username='estudiante1').exists():
            User.objects.create_user('estudiante1', 'estudiante1@test.com', '123456')
            User.objects.create_user('estudiante2', 'estudiante2@test.com', '123456')
            User.objects.create_user('profesor1', 'profesor1@test.com', '123456')
            self.stdout.write('✅ Usuarios de prueba creados')

        self.stdout.write(self.style.SUCCESS(f'🎉 ¡{total_cursos} cursos con contenido REAL generados!'))
