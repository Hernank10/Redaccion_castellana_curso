from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Carga lecciones de narrativa LIMPIAS'

    def handle(self, *args, **options):
        self.stdout.write('📚 Cargando lecciones de narrativa LIMPIAS...')
        
        course, _ = Course.objects.get_or_create(
            slug='narracion',
            defaults={
                'name': 'Fórmulas de Narración',
                'description': '100 técnicas de Fórmulas de Narración',
                'icon': '📖',
                'category': 'narration',
                'is_active': True
            }
        )
        
        # Eliminar todas las lecciones existentes de este curso
        course.lessons.all().delete()
        self.stdout.write('🗑️ Eliminadas lecciones anteriores')
        
        lessons = [
            ('Érase una vez', 'Inicio de cuento tradicional', '', 'Fórmula clásica de inicio'),
            ('Había una vez', 'Inicio de cuento infantil', '', 'Fórmula tradicional'),
            ('Cuando...', 'Introducción temporal', '', 'Marca el momento de la acción'),
            ('En un lugar de la Mancha', 'Inicio literario clásico', 'El Quijote', 'Apertura de novela'),
            ('Hace mucho tiempo', 'Distancia temporal', '', 'Crea ambientación lejana'),
            ('En aquellos días', 'Referencia histórica', '', 'Ambientación en el pasado'),
            ('De repente', 'Cambio brusco en la acción', '', 'Marca un giro inesperado'),
            ('Mientras tanto', 'Simultaneidad de acciones', '', 'Acción paralela'),
            ('Al final', 'Conclusión de la narración', '', 'Cierra el relato'),
            ('Y así fue como', 'Final explicativo', '', 'Explica el desenlace'),
            ('Entonces', 'Secuencia temporal', '', 'Marca continuación de la acción'),
            ('Después de', 'Posterioridad temporal', '', 'Orden cronológico'),
            ('Antes de', 'Anterioridad temporal', '', 'Orden cronológico'),
            ('Durante', 'Transcurso de tiempo', '', 'Duración de la acción'),
            ('Mientras', 'Simultaneidad', '', 'Acción concurrente'),
            ('Apenas', 'Inmediatez temporal', '', 'Acción reciente'),
            ('Tan pronto como', 'Inmediatez', '', 'Acción inmediata'),
            ('En cuanto', 'Inmediatez', '', 'Acción inmediata'),
            ('Acto seguido', 'Continuación inmediata', '', 'Acción siguiente sin pausa'),
            ('De inmediato', 'Reacción rápida', '', 'Acción sin demora'),
            ('Sin demora', 'Urgencia en la acción', '', 'Acción sin pausa'),
            ('De golpe', 'Sorpresa inesperada', '', 'Cambio repentino'),
            ('Por fin', 'Resolución esperada', '', 'Fin de la espera'),
            ('Al cabo de', 'Transcurso de tiempo', '', 'Paso del tiempo'),
            ('Días después', 'Salto temporal', '', 'Avance en el tiempo'),
            ('Al amanecer', 'Marca de tiempo', '', 'Inicio del día'),
            ('Al anochecer', 'Marca de tiempo', '', 'Final del día'),
            ('En aquel entonces', 'Tiempo pasado', '', 'Referencia al pasado'),
            ('Ya era hora de', 'Momento esperado', '', 'Llegada del momento'),
            ('Por último', 'Cierre de secuencia', '', 'Final de la enumeración'),
        ]
        
        order = 1
        for root, meaning, example, breakdown in lessons:
            Lesson.objects.create(
                course=course,
                order=order,
                title=root,
                root=root,
                meaning=meaning,
                example=example or f'"{root}" en una narración',
                breakdown=breakdown,
                is_active=True
            )
            order += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ {len(lessons)} lecciones LIMPIAS cargadas en {course.name}'))
