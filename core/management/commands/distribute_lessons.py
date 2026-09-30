import re
from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Distribuye lecciones de "Técnicas Generales" en cursos específicos'

    def handle(self, *args, **options):
        self.stdout.write('📚 Distribuyendo lecciones...')
        
        general = Course.objects.get(slug='general')
        lessons = general.lessons.filter(is_active=True)
        
        if not lessons:
            self.stdout.write('⚠️ No hay lecciones en Técnicas Generales')
            return
        
        # Mapeo de palabras clave a cursos
        keyword_map = {
            'redaccion': 'descripcion',
            'escritura': 'descripcion',
            'ortografia': 'puntuacion',
            'gramatica': 'argumentacion',
            'sintaxis': 'argumentacion',
            'lectura': 'narracion',
            'texto': 'exposicion',
            'ensayo': 'exposicion',
            'argumento': 'argumentacion',
            'cuento': 'narracion',
            'historia': 'narracion',
            'narrativa': 'narracion',
            'descriptivo': 'descripcion',
            'expositivo': 'exposicion',
            'poesia': 'retorica',
            'literatura': 'retorica',
            'metafora': 'retorica',
            'figura': 'retorica',
            'comunicacion': 'conectores',
            'discurso': 'conectores',
            'comparacion': 'comparacion',
            'comparativo': 'comparacion',
            'fonetica': 'fonetica',
            'sonido': 'fonetica',
            'pronunciacion': 'fonetica',
            'raiz': 'etimologia',
            'etimologia': 'etimologia',
            'prefijo': 'etimologia',
            'sufijo': 'etimologia',
            'verbo': 'perifrasis',
            'perifrasis': 'perifrasis',
            'tiempo verbal': 'perifrasis',
        }
        
        moved = 0
        for lesson in lessons:
            text = (lesson.root + ' ' + lesson.meaning + ' ' + lesson.example + ' ' + lesson.breakdown).lower()
            
            # Buscar coincidencias
            best_match = None
            best_score = 0
            
            for keyword, slug in keyword_map.items():
                if keyword in text:
                    # Dar más peso a coincidencias en el título
                    if keyword in lesson.root.lower():
                        score = 3
                    else:
                        score = 1
                    
                    if score > best_score:
                        best_score = score
                        best_match = slug
            
            # Si hay coincidencia, mover al curso
            if best_match and best_score >= 1:
                try:
                    target = Course.objects.get(slug=best_match)
                    lesson.course = target
                    lesson.save()
                    moved += 1
                except:
                    pass
        
        self.stdout.write(self.style.SUCCESS(f'✅ {moved} lecciones redistribuidas'))
        
        # Mostrar resultados
        self.stdout.write('\n📊 Distribución final:')
        for course in Course.objects.all():
            count = course.lessons.count()
            if count > 0:
                self.stdout.write(f'  {course.icon} {course.name}: {count} lecciones')
