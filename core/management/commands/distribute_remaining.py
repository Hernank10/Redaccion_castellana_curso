import re
from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Distribuye las lecciones restantes de Técnicas Generales'

    def handle(self, *args, **options):
        self.stdout.write('📚 Distribuyendo lecciones restantes...')
        
        general = Course.objects.get(slug='general')
        lessons = general.lessons.filter(is_active=True)
        
        if not lessons:
            self.stdout.write('⚠️ No hay lecciones en Técnicas Generales')
            return
        
        keyword_map = {
            'raíz': 'etimologia', 'raiz': 'etimologia', 'etimología': 'etimologia',
            'griego': 'etimologia', 'latín': 'etimologia', 'prefijo': 'etimologia',
            'sufijo': 'etimologia', 'lexema': 'etimologia', 'morfema': 'etimologia',
            'perífrasis': 'perifrasis', 'perifrasis': 'perifrasis', 'verbo': 'perifrasis',
            'infinitivo': 'perifrasis', 'gerundio': 'perifrasis',
            'fonética': 'fonetica', 'fonetica': 'fonetica', 'fonología': 'fonetica',
            'sonido': 'fonetica', 'vocal': 'fonetica', 'consonante': 'fonetica',
            'puntuación': 'puntuacion', 'coma': 'puntuacion', 'punto': 'puntuacion',
            'signo': 'puntuacion', 'paréntesis': 'puntuacion', 'guión': 'puntuacion',
            'conector': 'conectores', 'anáfora': 'conectores', 'catáfora': 'conectores',
            'cohesión': 'conectores', 'enlace': 'conectores',
            'retórica': 'retorica', 'metáfora': 'retorica', 'símil': 'retorica',
            'hipérbole': 'retorica', 'ironía': 'retorica', 'figura': 'retorica',
            'comparación': 'comparacion', 'comparativo': 'comparacion',
            'superlativo': 'comparacion', 'igualdad': 'comparacion',
            'descripción': 'descripcion', 'adjetivo': 'descripcion',
            'exposición': 'exposicion', 'explicar': 'exposicion', 'definir': 'exposicion',
            'ensayo': 'exposicion', 'argumentación': 'argumentacion',
            'argumento': 'argumentacion', 'tesis': 'argumentacion',
            'persuadir': 'argumentacion', 'razonamiento': 'argumentacion',
            'sintaxis': 'argumentacion', 'gramática': 'argumentacion',
            'narración': 'narracion', 'cuento': 'narracion', 'historia': 'narracion',
            'relato': 'narracion', 'trama': 'narracion', 'personaje': 'narracion',
            'lectura': 'narracion', 'texto': 'narracion',
        }
        
        moved = 0
        for lesson in lessons:
            text = (lesson.root + ' ' + lesson.meaning + ' ' + lesson.example + ' ' + lesson.breakdown).lower()
            
            best_match = None
            best_score = 0
            
            for keyword, slug in keyword_map.items():
                if keyword in text:
                    score = 2
                    if keyword in lesson.root.lower():
                        score = 4
                    if score > best_score:
                        best_score = score
                        best_match = slug
            
            if best_match and best_score >= 2:
                try:
                    target = Course.objects.get(slug=best_match)
                    # Verificar si ya existe una lección similar
                    exists = target.lessons.filter(root__iexact=lesson.root[:30]).exists()
                    if not exists:
                        # Obtener el último order del curso destino
                        last_order = target.lessons.order_by('-order').first()
                        new_order = (last_order.order + 1) if last_order else 1
                        lesson.course = target
                        lesson.order = new_order
                        lesson.save()
                        moved += 1
                except Exception as e:
                    self.stdout.write(f'⚠️ Error: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ {moved} lecciones redistribuidas'))
        
        # Mostrar resultados
        self.stdout.write('\n📊 Distribución final:')
        for course in Course.objects.all():
            count = course.lessons.count()
            if count > 0:
                self.stdout.write(f'  {course.icon} {course.name}: {count} lecciones')
