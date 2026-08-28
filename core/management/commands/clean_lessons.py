import re
from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Limpia lecciones corruptas y reorganiza'

    def handle(self, *args, **options):
        self.stdout.write('🧹 Limpiando lecciones corruptas...')
        
        # Palabras que indican datos corruptos
        corrupt_patterns = [
            r'\$\{',
            r'g\.lang',
            r'let totalScore',
            r'// =',
            r'multipleChoiceGame',
            r'<script',
            r'</script>',
            r'function',
            r'return',
            r'export',
            r'import',
            r'const',
            r'var ',
            r'let ',
        ]
        
        total_cleaned = 0
        total_deleted = 0
        
        for course in Course.objects.all():
            lessons = course.lessons.filter(is_active=True)
            for lesson in lessons:
                text = (lesson.root + ' ' + lesson.meaning + ' ' + lesson.example + ' ' + lesson.breakdown)
                
                # Verificar si es corrupto
                is_corrupt = False
                for pattern in corrupt_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        is_corrupt = True
                        break
                
                # También verificar si es muy corto o sin sentido
                if not is_corrupt and len(lesson.root) < 3 and len(lesson.meaning) < 10:
                    is_corrupt = True
                
                if is_corrupt:
                    # Intentar limpiar extrayendo información útil
                    cleaned_root = lesson.root
                    cleaned_meaning = lesson.meaning
                    
                    # Si el root contiene código, intentar extraer texto entre comillas
                    if re.search(r'"([^"]+)"', lesson.root):
                        match = re.search(r'"([^"]+)"', lesson.root)
                        if match:
                            cleaned_root = match.group(1)[:50]
                    
                    if re.search(r'"([^"]+)"', lesson.meaning):
                        match = re.search(r'"([^"]+)"', lesson.meaning)
                        if match:
                            cleaned_meaning = match.group(1)[:200]
                    
                    # Si después de limpiar sigue siendo corrupto, eliminar
                    if len(cleaned_root) < 2 or len(cleaned_meaning) < 5:
                        lesson.delete()
                        total_deleted += 1
                    else:
                        lesson.root = cleaned_root
                        lesson.meaning = cleaned_meaning
                        lesson.example = ''
                        lesson.breakdown = ''
                        lesson.save()
                        total_cleaned += 1
        
        # Reordenar todas las lecciones
        for course in Course.objects.all():
            lessons = course.lessons.filter(is_active=True).order_by('id')
            order = 1
            for lesson in lessons:
                lesson.order = order
                lesson.save()
                order += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Limpiadas: {total_cleaned}, Eliminadas: {total_deleted}'))
        
        # Mostrar estadísticas
        self.stdout.write('\n📊 Estadísticas finales:')
        for course in Course.objects.all():
            count = course.lessons.count()
            self.stdout.write(f'  {course.name}: {count} lecciones')
