from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Añade lecciones de etimología reales'

    def handle(self, *args, **options):
        self.stdout.write('📚 Añadiendo lecciones de etimología...')
        
        course, _ = Course.objects.get_or_create(
            slug='etimologia',
            defaults={
                'name': 'Raíces y Etimología',
                'description': '100 técnicas de Raíces y Etimología',
                'icon': '📜',
                'category': 'etymology',
                'is_active': True
            }
        )
        
        # Lecciones de etimología reales
        lessons_data = [
            ('bio-', 'vida', 'biología', 'estudio de la vida'),
            ('geo-', 'tierra', 'geografía', 'descripción de la tierra'),
            ('logos', 'estudio, palabra', 'psicología', 'estudio de la mente'),
            ('pathos', 'sentimiento', 'empatía', 'capacidad de sentir con otros'),
            ('chronos', 'tiempo', 'crónico', 'relativo al tiempo'),
            ('philos', 'amor', 'filantropía', 'amor a la humanidad'),
            ('sophia', 'sabiduría', 'filosofía', 'amor a la sabiduría'),
            ('demos', 'pueblo', 'democracia', 'gobierno del pueblo'),
            ('kratos', 'poder', 'aristocracia', 'gobierno de los mejores'),
            ('polis', 'ciudad', 'metrópolis', 'ciudad madre'),
            ('theos', 'dios', 'teología', 'estudio de dios'),
            ('anthropos', 'hombre', 'antropología', 'estudio del ser humano'),
            ('zoe', 'vida', 'zoología', 'estudio de los animales'),
            ('psyche', 'alma', 'psicología', 'estudio de la mente'),
            ('techne', 'arte', 'tecnología', 'estudio de la técnica'),
            ('phone', 'sonido', 'teléfono', 'sonido a distancia'),
            ('grapho', 'escribir', 'grafiti', 'escritura'),
            ('hydro', 'agua', 'hidroeléctrica', 'agua + electricidad'),
            ('pneuma', 'aliento', 'neumático', 'relativo al aire'),
            ('soma', 'cuerpo', 'somatización', 'expresión corporal'),
            ('glossa', 'lengua', 'glosario', 'lista de términos'),
            ('nomos', 'ley', 'economía', 'ley de la casa'),
            ('ergon', 'trabajo', 'energía', 'capacidad de trabajar'),
            ('dynamis', 'fuerza', 'dinámico', 'relativo a la fuerza'),
            ('telos', 'fin', 'teleología', 'estudio de los fines'),
            ('meta', 'más allá', 'metafísica', 'más allá de la física'),
            ('para', 'junto a', 'paralelo', 'junto a otro'),
            ('anti', 'contra', 'antídoto', 'contra el veneno'),
            ('hyper', 'sobre', 'hiperactivo', 'sobreactivo'),
            ('hypo', 'debajo', 'hipotermia', 'debajo de temperatura'),
        ]
        
        count = 0
        for root, meaning, example, breakdown in lessons_data:
            # Verificar si ya existe
            if Lesson.objects.filter(course=course, root__icontains=root).exists():
                continue
            
            Lesson.objects.create(
                course=course,
                order=Lesson.objects.filter(course=course).count() + 1,
                title=root,
                root=root,
                meaning=meaning,
                example=example,
                breakdown=breakdown,
                is_active=True
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ {count} lecciones de etimología añadidas'))
