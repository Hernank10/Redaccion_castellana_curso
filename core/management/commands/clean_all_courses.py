from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Limpia TODOS los cursos de datos corruptos'

    def handle(self, *args, **options):
        self.stdout.write('🧹 Limpiando TODOS los cursos...')
        
        corrupt_patterns = ['${', 'g.lang', 'let totalScore', '// =', 'multipleChoiceGame', '<script', 'function', 'return', 'export', 'import', 'const', 'var ', 'let ', 'Emparejados', 'Restantes', 'Tema sugerido', 'tags.map']
        
        total_deleted = 0
        
        for course in Course.objects.all():
            count_before = course.lessons.count()
            deleted = 0
            
            for lesson in course.lessons.all():
                text = (lesson.root + ' ' + lesson.meaning + ' ' + lesson.example + ' ' + lesson.breakdown)
                is_corrupt = any(p in text for p in corrupt_patterns)
                if is_corrupt or len(lesson.root) < 2 or len(lesson.meaning) < 2:
                    lesson.delete()
                    deleted += 1
            
            total_deleted += deleted
            if deleted > 0:
                self.stdout.write(f'  {course.name}: {deleted} lecciones corruptas eliminadas')
        
        # Reordenar todas las lecciones
        for course in Course.objects.all():
            lessons = course.lessons.filter(is_active=True).order_by('id')
            order = 1
            for lesson in lessons:
                lesson.order = order
                lesson.save()
                order += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Total eliminadas: {total_deleted} lecciones corruptas'))
        
        # Mostrar estadísticas finales
        self.stdout.write('\n📊 Estadísticas finales:')
        for course in Course.objects.all():
            count = course.lessons.count()
            if count > 0:
                self.stdout.write(f'  {course.icon} {course.name}: {count} lecciones')
