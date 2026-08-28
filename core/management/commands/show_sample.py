from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Muestra una muestra de lecciones de cada curso'

    def handle(self, *args, **options):
        for course in Course.objects.all():
            count = course.lessons.count()
            if count == 0:
                continue
            self.stdout.write(f'\n📚 {course.name} ({count} lecciones):')
            for lesson in course.lessons.all()[:5]:
                self.stdout.write(f'  {lesson.order}. {lesson.root[:50]}')
            if count > 5:
                self.stdout.write(f'  ... y {count - 5} más')
