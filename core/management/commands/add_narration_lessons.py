from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Añade lecciones de narrativa reales'

    def handle(self, *args, **options):
        self.stdout.write('📚 Añadiendo lecciones de narrativa...')
        
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
        
        lessons_data = [
            ('Érase una vez', 'Inicio de cuento tradicional', '', 'Fórmula clásica de inicio'),
            ('Cuando...', 'Introducción temporal', '', 'Marca el momento de la acción'),
            ('Había una vez', 'Inicio de cuento infantil', '', 'Fórmula tradicional'),
            ('En un lugar de la Mancha', 'Inicio literario', 'El Quijote', 'Apertura de novela'),
            ('Hace mucho tiempo', 'Distancia temporal', '', 'Crea ambientación'),
            ('En aquellos días', 'Referencia histórica', '', 'Ambientación temporal'),
            ('De repente', 'Cambio brusco', '', 'Marca un giro'),
            ('Mientras tanto', 'Simultaneidad', '', 'Acción paralela'),
            ('Al final', 'Conclusión', '', 'Cierra la narración'),
            ('Y así fue como', 'Final explicativo', '', 'Explica el desenlace'),
            ('Lo que pasó fue', 'Introducción causal', '', 'Explica el origen'),
            ('Entonces', 'Secuencia temporal', '', 'Marca continuación'),
            ('Después de', 'Posterioridad', '', 'Orden temporal'),
            ('Antes de', 'Anterioridad', '', 'Orden temporal'),
            ('Durante', 'Transcurso', '', 'Duración de la acción'),
            ('Mientras', 'Simultaneidad', '', 'Acción concurrente'),
            ('Apenas', 'Inmediatez', '', 'Acción reciente'),
            ('Tan pronto como', 'Inmediatez', '', 'Acción inmediata'),
            ('En cuanto', 'Inmediatez', '', 'Acción inmediata'),
            ('Acto seguido', 'Continuación', '', 'Acción siguiente'),
            ('De inmediato', 'Reacción', '', 'Acción rápida'),
            ('Sin demora', 'Urgencia', '', 'Acción sin pausa'),
            ('De golpe', 'Sorpresa', '', 'Cambio inesperado'),
            ('Por fin', 'Resolución', '', 'Fin de la espera'),
            ('Al cabo de', 'Transcurso', '', 'Paso del tiempo'),
        ]
        
        count = 0
        for root, meaning, example, breakdown in lessons_data:
            if Lesson.objects.filter(course=course, root__icontains=root).exists():
                continue
            
            Lesson.objects.create(
                course=course,
                order=Lesson.objects.filter(course=course).count() + 1,
                title=root,
                root=root,
                meaning=meaning,
                example=example or f'"{root}" en una narración',
                breakdown=breakdown,
                is_active=True
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ {count} lecciones de narrativa añadidas'))
