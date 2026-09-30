import os
import re
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Carga HTMLs a nuevos cursos'

    def handle(self, *args, **options):
        self.stdout.write('📂 Cargando HTMLs a nuevos cursos...')
        
        # Mapeo de palabras clave a nuevos cursos
        course_map = {
            'gramatica': 'gramatica',
            'gramática': 'gramatica',
            'sintaxis': 'sintaxis',
            'sintáctico': 'sintaxis',
            'literatura': 'literatura',
            'poesia': 'poesia',
            'poética': 'poesia',
            'ortografia': 'ortografia',
            'ortografía': 'ortografia',
            'redaccion avanzada': 'redaccion_avanzada',
            'redacción avanzada': 'redaccion_avanzada',
            'comunicacion': 'comunicacion',
            'comunicación': 'comunicacion',
            'academica': 'academica',
            'académica': 'academica',
            'cientifica': 'cientifica',
            'científica': 'cientifica',
            'periodistica': 'periodistica',
            'periodística': 'periodistica',
        }
        
        search_paths = [
            '/home/codespace/backup_htmls',
            '/workspaces/Redaccion_castellana_curso/ejercicios_completos-lengua-castellana',
        ]
        
        total_lessons = 0
        
        for base_path in search_paths:
            if not os.path.exists(base_path):
                continue
            
            self.stdout.write(f'📂 Buscando en: {base_path}')
            
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if not file.endswith('.html'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    file_lower = file.lower()
                    
                    # Determinar curso por palabras clave
                    course_slug = 'general'
                    for key, slug in course_map.items():
                        if key in file_lower:
                            course_slug = slug
                            break
                    
                    # Si no es un curso nuevo, saltar
                    if course_slug in ['general']:
                        continue
                    
                    try:
                        course = Course.objects.get(slug=course_slug)
                    except:
                        continue
                    
                    lessons = self.extract_lessons(file_path)
                    
                    if lessons:
                        saved = self.save_lessons(lessons, course)
                        if saved > 0:
                            total_lessons += saved
                            self.stdout.write(f'  ✅ {file}: {saved} lecciones → {course.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 TOTAL: {total_lessons} lecciones cargadas en nuevos cursos'))

    def extract_lessons(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return []
        
        lessons = []
        
        # Buscar en scripts
        script_pattern = r'<script[^>]*>([\s\S]*?)</script>'
        scripts = re.findall(script_pattern, content)
        
        for script in scripts:
            patterns = [
                r'\{[^{}]*"root"[^{}]*"meaning"[^{}]*\}',
                r'\{[^{}]*"raiz"[^{}]*"significado"[^{}]*\}',
                r'\{[^{}]*"técnica"[^{}]*"descripción"[^{}]*\}',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, script)
                for match in matches:
                    try:
                        data_str = re.sub(r'(\w+):', r'"\1":', match)
                        data_str = re.sub(r"'", '"', data_str)
                        data = json.loads(data_str)
                        
                        root = data.get('root') or data.get('raiz') or data.get('técnica') or ''
                        meaning = data.get('meaning') or data.get('significado') or data.get('descripción') or ''
                        
                        if root and meaning and len(root) > 2 and len(meaning) > 2:
                            lessons.append({
                                'root': str(root)[:100],
                                'meaning': str(meaning)[:500],
                                'example': str(data.get('example', ''))[:500],
                                'breakdown': str(data.get('breakdown', ''))[:500]
                            })
                    except:
                        pass
        
        return lessons

    def save_lessons(self, lessons, course):
        saved = 0
        for data in lessons:
            if not data['root'] or not data['meaning']:
                continue
            
            if Lesson.objects.filter(course=course, root__iexact=data['root'][:30]).exists():
                continue
            
            with transaction.atomic():
                last = course.lessons.order_by('-order').first()
                new_order = (last.order + 1) if last else 1
                
                Lesson.objects.create(
                    course=course,
                    order=new_order,
                    title=data['root'][:80],
                    root=data['root'][:80],
                    meaning=data['meaning'][:300],
                    example=data['example'][:300] if data['example'] else '',
                    breakdown=data['breakdown'][:300] if data['breakdown'] else '',
                    is_active=True
                )
                saved += 1
        
        return saved
