from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Reordena todas las lecciones de todos los cursos'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Reordenando todas las lecciones...')
        
        for course in Course.objects.all():
            lessons = course.lessons.filter(is_active=True).order_by('id')
            order = 1
            for lesson in lessons:
                lesson.order = order
                lesson.save()
                order += 1
            self.stdout.write(f'  {course.name}: {order - 1} lecciones reordenadas')
        
        self.stdout.write(self.style.SUCCESS('✅ ¡Reordenación completada!'))
