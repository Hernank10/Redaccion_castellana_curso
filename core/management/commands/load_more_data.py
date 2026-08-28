import os
import json
import re
from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Carga más datos desde archivos HTML y JSON'

    def handle(self, *args, **options):
        self.stdout.write('📂 Cargando más datos...')
        
        base_path = '/workspaces/Redaccion_castellana_curso/ejercicios_completos-lengua-castellana'
        if not os.path.exists(base_path):
            self.stdout.write('⚠️ Ruta no encontrada')
            return
        
        total = 0
        for root, dirs, files in os.walk(base_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                if file.endswith('.json'):
                    lessons = self.process_json(file_path)
                    total += self.save_lessons(lessons, file_path)
                    self.stdout.write(f'  ✅ {file}: {len(lessons)} lecciones')
                
                elif file.endswith('.html'):
                    lessons = self.process_html(file_path)
                    total += self.save_lessons(lessons, file_path)
                    self.stdout.write(f'  ✅ {file}: {len(lessons)} lecciones')
        
        self.stdout.write(self.style.SUCCESS(f'🎉 Total cargado: {total} lecciones nuevas'))

    def process_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
        except:
            return []
        
        lessons = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    root = item.get('root') or item.get('title') or item.get('name') or ''
                    meaning = item.get('meaning') or item.get('description') or item.get('descripcion') or ''
                    if root and meaning:
                        lessons.append({
                            'root': str(root)[:100],
                            'meaning': str(meaning)[:500],
                            'example': str(item.get('example', ''))[:500],
                            'breakdown': str(item.get('breakdown', ''))[:500]
                        })
        return lessons

    def process_html(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return []
        
        lessons = []
        
        # Buscar patrones en scripts
        script_pattern = r'<script[^>]*>([\s\S]*?)</script>'
        for match in re.finditer(script_pattern, content):
            script = match.group(1)
            pattern = r'\{[^{}]*"(?:root|raiz|title|tecnica|técnica)"[^{}]*"(?:meaning|significado|descripcion|descripción)"[^{}]*\}'
            for m in re.finditer(pattern, script):
                try:
                    data_str = m.group()
                    data_str = re.sub(r'(\w+):', r'"\1":', data_str)
                    data_str = re.sub(r"'", '"', data_str)
                    data = json.loads(data_str)
                    
                    root = data.get('root') or data.get('raiz') or data.get('title') or data.get('tecnica') or ''
                    meaning = data.get('meaning') or data.get('significado') or data.get('descripcion') or ''
                    
                    if root and meaning:
                        lessons.append({
                            'root': str(root)[:100],
                            'meaning': str(meaning)[:500],
                            'example': str(data.get('example', ''))[:500],
                            'breakdown': str(data.get('breakdown', ''))[:500]
                        })
                except:
                    pass
        
        return lessons

    def save_lessons(self, lessons, file_path):
        if not lessons:
            return 0
        
        # Determinar curso
        file_name = os.path.basename(file_path).lower()
        slug = 'general'
        
        course_map = {
            'etimologia': 'etimologia',
            'perifrasis': 'perifrasis',
            'fonetica': 'fonetica',
            'puntuacion': 'puntuacion',
            'conectores': 'conectores',
            'retorica': 'retorica',
            'comparacion': 'comparacion',
            'descripcion': 'descripcion',
            'exposicion': 'exposicion',
            'argumentacion': 'argumentacion',
            'narracion': 'narracion',
        }
        
        for key, value in course_map.items():
            if key in file_name:
                slug = value
                break
        
        try:
            course = Course.objects.get(slug=slug)
        except:
            course = Course.objects.get(slug='general')
        
        saved = 0
        for data in lessons:
            count = Lesson.objects.filter(course=course).count()
            Lesson.objects.create(
                course=course,
                order=count + 1,
                title=data['root'][:100],
                root=data['root'][:100],
                meaning=data['meaning'][:500],
                example=data['example'][:500],
                breakdown=data['breakdown'][:500],
                is_active=True
            )
            saved += 1
        
        return saved
