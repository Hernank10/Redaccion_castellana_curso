from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Reordena todas las lecciones de todos los cursos (sin duplicados)'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Reordenando todas las lecciones...')
        
        for course in Course.objects.all():
            with transaction.atomic():
                lessons = course.lessons.filter(is_active=True).order_by('id')
                
                # Verificar duplicados de order
                orders = {}
                for lesson in lessons:
                    if lesson.order in orders:
                        orders[lesson.order].append(lesson.id)
                    else:
                        orders[lesson.order] = [lesson.id]
                
                # Eliminar duplicados
                for order, ids in orders.items():
                    if len(ids) > 1:
                        for lesson_id in ids[1:]:
                            Lesson.objects.get(id=lesson_id).delete()
                
                # Reordenar
                remaining = course.lessons.filter(is_active=True).order_by('id')
                new_order = 1
                for lesson in remaining:
                    lesson.order = new_order
                    lesson.save()
                    new_order += 1
                
                self.stdout.write(f'  {course.name}: {new_order - 1} lecciones reordenadas')
        
        self.stdout.write(self.style.SUCCESS('✅ ¡Reordenación completada!'))
