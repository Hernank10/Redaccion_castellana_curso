from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Carga lecciones de etimología LIMPIAS'

    def handle(self, *args, **options):
        self.stdout.write('📚 Cargando lecciones de etimología LIMPIAS...')
        
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
        
        # Eliminar todas las lecciones existentes de este curso
        course.lessons.all().delete()
        self.stdout.write('🗑️ Eliminadas lecciones anteriores')
        
        # Lecciones LIMPIAS de etimología
        lessons = [
            ('bio-', 'vida', 'biología', 'estudio de la vida'),
            ('geo-', 'tierra', 'geografía', 'descripción de la tierra'),
            ('logos', 'estudio, palabra', 'psicología', 'estudio de la mente'),
            ('pathos', 'sentimiento, enfermedad', 'empatía', 'capacidad de sentir con otros'),
            ('chronos', 'tiempo', 'crónico', 'relativo al tiempo'),
            ('philos', 'amor', 'filantropía', 'amor a la humanidad'),
            ('sophia', 'sabiduría', 'filosofía', 'amor a la sabiduría'),
            ('demos', 'pueblo', 'democracia', 'gobierno del pueblo'),
            ('kratos', 'poder, fuerza', 'aristocracia', 'gobierno de los mejores'),
            ('polis', 'ciudad', 'metrópolis', 'ciudad madre'),
            ('theos', 'dios', 'teología', 'estudio de dios'),
            ('anthropos', 'hombre, humano', 'antropología', 'estudio del ser humano'),
            ('zoe', 'vida', 'zoología', 'estudio de los animales'),
            ('psyche', 'alma, mente', 'psicología', 'estudio de la mente'),
            ('techne', 'arte, técnica', 'tecnología', 'estudio de la técnica'),
            ('phone', 'sonido, voz', 'teléfono', 'sonido a distancia'),
            ('grapho', 'escribir, dibujar', 'grafiti', 'escritura'),
            ('hydro', 'agua', 'hidroeléctrica', 'agua y electricidad'),
            ('pneuma', 'aliento, espíritu', 'neumático', 'relativo al aire'),
            ('soma', 'cuerpo', 'somatización', 'expresión corporal'),
            ('glossa', 'lengua, lenguaje', 'glosario', 'lista de términos'),
            ('nomos', 'ley, norma', 'economía', 'ley de la casa'),
            ('ergon', 'trabajo, energía', 'energía', 'capacidad de trabajar'),
            ('dynamis', 'fuerza, poder', 'dinámico', 'relativo a la fuerza'),
            ('telos', 'fin, objetivo', 'teleología', 'estudio de los fines'),
            ('meta', 'más allá', 'metafísica', 'más allá de la física'),
            ('para', 'junto a, al lado de', 'paralelo', 'junto a otro'),
            ('anti', 'contra', 'antídoto', 'contra el veneno'),
            ('hyper', 'sobre, por encima', 'hiperactivo', 'sobreactivo'),
            ('hypo', 'debajo, por debajo', 'hipotermia', 'debajo de temperatura'),
            ('aqua', 'agua', 'acuífero', 'que lleva agua'),
            ('terra', 'tierra', 'terrestre', 'relativo a la tierra'),
            ('corpus', 'cuerpo', 'corporal', 'relativo al cuerpo'),
            ('caput', 'cabeza', 'capital', 'relativo a la cabeza'),
            ('manus', 'mano', 'manuscrito', 'escrito a mano'),
            ('pes', 'pie', 'pedestre', 'relativo al pie'),
            ('pectus', 'pecho', 'pectoral', 'relativo al pecho'),
            ('os', 'hueso', 'óseo', 'relativo al hueso'),
            ('dens', 'diente', 'dentista', 'profesional de los dientes'),
            ('unguis', 'uña', 'ungulado', 'que tiene uñas'),
            ('lux', 'luz', 'lúcido', 'que tiene luz'),
            ('vox', 'voz', 'vocación', 'llamada de la voz'),
            ('pax', 'paz', 'pacífico', 'que tiene paz'),
            ('lex', 'ley', 'legal', 'relativo a la ley'),
            ('rex', 'rey', 'real', 'relativo al rey'),
            ('salus', 'salud', 'salubridad', 'cualidad de saludable'),
            ('virtus', 'valor, virtud', 'virtual', 'en potencia'),
            ('fortuna', 'suerte', 'afortunado', 'que tiene suerte'),
            ('amor', 'amor', 'amistad', 'relación de amor'),
        ]
        
        order = 1
        for root, meaning, example, breakdown in lessons:
            Lesson.objects.create(
                course=course,
                order=order,
                title=root,
                root=root,
                meaning=meaning,
                example=example,
                breakdown=breakdown,
                is_active=True
            )
            order += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ {len(lessons)} lecciones LIMPIAS cargadas en {course.name}'))
