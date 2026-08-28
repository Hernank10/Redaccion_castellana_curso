from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Corrige duplicados y reordena lecciones'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Corrigiendo duplicados...')
        
        for course in Course.objects.all():
            lessons = course.lessons.all().order_by('order')
            
            # Reasignar órdenes secuencialmente
            order = 1
            for lesson in lessons:
                lesson.order = order
                lesson.save()
                order += 1
            
            self.stdout.write(f'✅ {course.name}: {order - 1} lecciones reordenadas')
        
        self.stdout.write(self.style.SUCCESS('🎉 ¡Corrección completada!'))
