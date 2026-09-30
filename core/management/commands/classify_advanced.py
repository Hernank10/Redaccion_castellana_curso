import re
from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Clasifica lecciones avanzadamente usando más palabras clave'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Clasificando lecciones avanzadamente...')
        
        # Mapeo de palabras clave a cursos (más completo)
        keywords = {
            'etimologia': [
                'raíz', 'raiz', 'etimología', 'etimologia', 'griego', 'latín', 'latino',
                'prefijo', 'sufijo', 'lexema', 'morfema', 'proto', 'indoeuropeo',
                'ἀπό', 'κατά', 'μετά', 'παρά', 'σύν', 'anti', 'bio', 'geo', 'logos',
                'pathos', 'chronos', 'psyche', 'techne', 'phone', 'grapho', 'hydro'
            ],
            'perifrasis': [
                'perífrasis', 'perifrasis', 'verbal', 'infinitivo', 'gerundio', 'participio',
                'obligación', 'posibilidad', 'tener que', 'deber', 'poder', 'ir a',
                'estar', 'andar', 'venir', 'volver', 'acabar', 'terminar'
            ],
            'fonetica': [
                'fonética', 'fonetica', 'fonología', 'fonologia', 'AFI', 'vocal', 'consonante',
                'sonido', 'pronunciación', 'acento', 'sílaba', 'diptongo', 'triptongo',
                'oclusiva', 'fricativa', 'nasal', 'lateral', 'vibrante'
            ],
            'puntuacion': [
                'puntuación', 'puntuacion', 'coma', 'punto', 'signo', 'interrogación',
                'exclamación', 'paréntesis', 'guión', 'puntos suspensivos', 'dos puntos',
                'punto y coma', 'comillas', 'diéresis', 'tilde'
            ],
            'conectores': [
                'conector', 'conectores', 'anáfora', 'catáfora', 'cohesión', 'coherencia',
                'enlace', 'marcador', 'además', 'también', 'asimismo', 'igualmente',
                'por ejemplo', 'es decir', 'sin embargo', 'no obstante'
            ],
            'retorica': [
                'retórica', 'retorica', 'figura', 'metáfora', 'símil', 'hipérbole',
                'ironía', 'antítesis', 'paradoja', 'oxímoron', 'personificación',
                'aliteración', 'anáfora', 'epífora', 'polisíndeton', 'asíndeton'
            ],
            'comparacion': [
                'comparación', 'comparacion', 'comparativo', 'superlativo', 'igualdad',
                'inferioridad', 'superioridad', 'tan como', 'más que', 'menos que',
                'igual que', 'mayor', 'menor', 'mejor', 'peor'
            ],
            'descripcion': [
                'descripción', 'descripcion', 'adjetivo', 'calificativo', 'describir',
                'cualidad', 'característica', 'atributo', 'propiedad', 'rasgo'
            ],
            'exposicion': [
                'exposición', 'exposicion', 'explicar', 'definir', 'aclarar', 'informar',
                'expositivo', 'presentar', 'describir', 'detallar', 'especificar'
            ],
            'argumentacion': [
                'argumentación', 'argumentacion', 'argumentar', 'persuadir', 'tesis',
                'razonamiento', 'evidencia', 'prueba', 'justificar', 'demostrar',
                'concluir', 'razón', 'motivo'
            ],
            'narracion': [
                'narración', 'narracion', 'narrar', 'cuento', 'historia', 'relato',
                'secuencia', 'trama', 'personaje', 'tiempo', 'espacio', 'acción',
                'suceso', 'evento', 'cronología'
            ]
        }
        
        general = Course.objects.get(slug='general')
        lessons = Lesson.objects.filter(course=general)
        
        if not lessons:
            self.stdout.write('⚠️ No hay lecciones en "Técnicas Generales"')
            return
        
        self.stdout.write(f'📚 Clasificando {lessons.count()} lecciones...')
        
        moved = 0
        for lesson in lessons:
            text = (lesson.root + ' ' + lesson.meaning + ' ' + lesson.example + ' ' + lesson.breakdown).lower()
            
            best_match = None
            best_score = 0
            
            for slug, words in keywords.items():
                score = sum(1 for word in words if word in text)
                if score > best_score:
                    best_score = score
                    best_match = slug
            
            # Si hay coincidencia, mover al curso
            if best_score >= 2 and best_match:
                try:
                    target_course = Course.objects.get(slug=best_match)
                    lesson.course = target_course
                    lesson.save()
                    moved += 1
                except:
                    pass
        
        self.stdout.write(self.style.SUCCESS(f'✅ {moved} lecciones clasificadas en otros cursos'))
        
        # Mostrar resultados
        self.stdout.write('\n📊 Distribución actual:')
        for course in Course.objects.all():
            count = course.lessons.count()
            bar = '█' * min(int(count / 10), 50)
            self.stdout.write(f'  {course.name}: {count} lecciones {bar}')
