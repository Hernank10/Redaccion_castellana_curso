import re
from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Clasifica las lecciones de "Técnicas Generales" en los cursos correspondientes'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Clasificando lecciones...')
        
        # Mapeo de palabras clave a cursos
        keywords = {
            'etimologia': ['raíz', 'raiz', 'etimología', 'etimologia', 'griego', 'latín', 'latino', 'prefijo', 'sufijo', 'lexema', 'morfema'],
            'perifrasis': ['perífrasis', 'perifrasis', 'verbal', 'infinitivo', 'gerundio', 'participio', 'obligación', 'posibilidad'],
            'fonetica': ['fonética', 'fonetica', 'fonología', 'fonologia', 'AFI', 'vocal', 'consonante', 'sonido', 'pronunciación'],
            'puntuacion': ['puntuación', 'puntuacion', 'coma', 'punto', 'signo', 'interrogación', 'exclamación', 'paréntesis', 'guión'],
            'conectores': ['conector', 'conectores', 'anáfora', 'catáfora', 'cohesión', 'coherencia', 'enlace'],
            'retorica': ['retórica', 'retorica', 'figura', 'metáfora', 'símil', 'hipérbole', 'ironía', 'antítesis', 'paradoja'],
            'comparacion': ['comparación', 'comparacion', 'comparativo', 'superlativo', 'igualdad', 'inferioridad', 'superioridad'],
            'descripcion': ['descripción', 'descripcion', 'adjetivo', 'calificativo', 'describir', 'cualidad'],
            'exposicion': ['exposición', 'exposicion', 'explicar', 'definir', 'aclarar', 'informar', 'expositivo'],
            'argumentacion': ['argumentación', 'argumentacion', 'argumentar', 'persuadir', 'tesis', 'razonamiento', 'evidencia'],
            'narracion': ['narración', 'narracion', 'narrar', 'cuento', 'historia', 'relato', 'secuencia', 'trama'],
        }
        
        # Obtener el curso general
        general = Course.objects.get(slug='general')
        lessons = Lesson.objects.filter(course=general)
        
        if not lessons:
            self.stdout.write('⚠️ No hay lecciones en "Técnicas Generales"')
            return
        
        self.stdout.write(f'📚 Clasificando {lessons.count()} lecciones...')
        
        moved = 0
        for lesson in lessons:
            text = (lesson.root + ' ' + lesson.meaning + ' ' + lesson.example + ' ' + lesson.breakdown).lower()
            
            # Buscar coincidencias
            best_match = None
            best_score = 0
            
            for slug, words in keywords.items():
                score = 0
                for word in words:
                    if word in text:
                        score += 1
                if score > best_score:
                    best_score = score
                    best_match = slug
            
            # Si hay coincidencia fuerte, mover al curso
            if best_score >= 2:
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
            self.stdout.write(f'  {course.name}: {count} lecciones')
