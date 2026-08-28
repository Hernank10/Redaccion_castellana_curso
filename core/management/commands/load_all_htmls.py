import os
import re
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Carga TODOS los archivos HTML a la base de datos'

    def handle(self, *args, **options):
        self.stdout.write('📂 Cargando TODOS los archivos HTML...')
        
        search_paths = [
            '/workspaces/Redaccion_castellana_curso/ejercicios_completos-lengua-castellana',
            '/home/codespace/backup_htmls',
            '/workspaces/Redaccion_castellana_curso/backup_htmls',
        ]
        
        total_lessons = 0
        files_processed = 0
        
        for base_path in search_paths:
            if not os.path.exists(base_path):
                continue
            
            self.stdout.write(f'📂 Buscando en: {base_path}')
            
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if not file.endswith('.html'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    lessons = self.extract_lessons(file_path)
                    
                    if lessons:
                        files_processed += 1
                        saved = self.save_lessons(lessons, file_path)
                        total_lessons += saved
                        if saved > 0:
                            self.stdout.write(f'  ✅ {file}: {saved} lecciones')
        
        # Reordenar TODAS las lecciones de TODOS los cursos
        self.stdout.write('\n🔧 Reordenando todas las lecciones...')
        for course in Course.objects.all():
            lessons = course.lessons.filter(is_active=True).order_by('id')
            order = 1
            for lesson in lessons:
                lesson.order = order
                lesson.save()
                order += 1
            if order > 1:
                self.stdout.write(f'  ✅ {course.name}: {order - 1} lecciones reordenadas')
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 TOTAL: {total_lessons} lecciones de {files_processed} archivos'))

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
        
        # Buscar en divs
        if not lessons:
            div_pattern = r'<div[^>]*class="[^"]*(?:tecnica|técnica|lesson|leccion|card|flashcard)[^"]*"[^>]*>([\s\S]*?)</div>'
            for match in re.finditer(div_pattern, content, re.I):
                div_content = match.group(1)
                text = re.sub(r'<[^>]+>', ' ', div_content)
                text = re.sub(r'\s+', ' ', text).strip()
                
                if ':' in text and len(text) > 20:
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if len(key) > 2 and len(value) > 5:
                            lessons.append({
                                'root': key[:80],
                                'meaning': value[:300],
                                'example': '',
                                'breakdown': ''
                            })
        
        return lessons

    def save_lessons(self, lessons, file_path):
        if not lessons:
            return 0
        
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
            'morfologia': 'etimologia',
            'sintaxis': 'argumentacion',
            'gramatica': 'argumentacion',
            'ortografia': 'puntuacion',
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
            if not data['root'] or not data['meaning']:
                continue
            
            # Verificar duplicados
            if Lesson.objects.filter(course=course, root__iexact=data['root'][:30]).exists():
                continue
            
            with transaction.atomic():
                # Obtener el último order + 1
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
