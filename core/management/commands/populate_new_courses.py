import os
import re
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Llena los cursos nuevos con contenido de los HTMLs'

    def handle(self, *args, **options):
        self.stdout.write('📚 Poblando cursos nuevos...')
        
        # Mapeo de archivos a cursos
        file_course_map = {
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
        courses_updated = set()
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
                    file_lower = file.lower()
                    
                    # Determinar curso
                    course_slug = None
                    for key, slug in file_course_map.items():
                        if key in file_lower:
                            course_slug = slug
                            break
                    
                    if not course_slug:
                        continue
                    
                    try:
                        course = Course.objects.get(slug=course_slug)
                    except:
                        continue
                    
                    files_processed += 1
                    lessons = self.extract_lessons_improved(file_path)
                    
                    if lessons:
                        saved = self.save_lessons(lessons, course)
                        if saved > 0:
                            total_lessons += saved
                            courses_updated.add(course.name)
                            self.stdout.write(f'  ✅ {file[:40]}: {saved} lecciones → {course.name}')
        
        # Reordenar todos los cursos
        self.stdout.write('\n🔧 Reordenando lecciones...')
        for course in Course.objects.all():
            lessons = course.lessons.filter(is_active=True).order_by('id')
            order = 1
            for lesson in lessons:
                lesson.order = order
                lesson.save()
                order += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 TOTAL: {total_lessons} lecciones cargadas de {files_processed} archivos'))
        self.stdout.write(f'📚 Cursos actualizados: {", ".join(courses_updated) if courses_updated else "Ninguno"}')

    def extract_lessons_improved(self, file_path):
        """Extrae lecciones mejorado - más robusto"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return []
        
        lessons = []
        
        # 1. Buscar en scripts
        script_pattern = r'<script[^>]*>([\s\S]*?)</script>'
        scripts = re.findall(script_pattern, content)
        
        for script in scripts:
            # Buscar arrays de objetos
            array_pattern = r'\[\s*\{[^]]*\}\s*\]'
            for match in re.finditer(array_pattern, script):
                try:
                    data_str = match.group()
                    # Limpiar y parsear
                    data_str = re.sub(r'(\w+):', r'"\1":', data_str)
                    data_str = re.sub(r"'", '"', data_str)
                    data = json.loads(data_str)
                    for item in data:
                        lesson = self.extract_lesson_from_item(item)
                        if lesson:
                            lessons.append(lesson)
                except:
                    pass
            
            # Buscar objetos individuales
            object_pattern = r'\{[^{}]*"root"[^{}]*"meaning"[^{}]*\}'
            for match in re.finditer(object_pattern, script):
                try:
                    data_str = match.group()
                    data_str = re.sub(r'(\w+):', r'"\1":', data_str)
                    data_str = re.sub(r"'", '"', data_str)
                    data = json.loads(data_str)
                    lesson = self.extract_lesson_from_item(data)
                    if lesson:
                        lessons.append(lesson)
                except:
                    pass
        
        # 2. Buscar en divs
        div_pattern = r'<div[^>]*class="[^"]*(?:tecnica|técnica|lesson|leccion|card|flashcard|item)[^"]*"[^>]*>([\s\S]*?)</div>'
        for match in re.finditer(div_pattern, content, re.I):
            div_content = match.group(1)
            text = re.sub(r'<[^>]+>', ' ', div_content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            if ':' in text and len(text) > 20:
                parts = text.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if len(key) > 2 and len(value) > 5 and len(key) < 100:
                        lessons.append({
                            'root': key[:80],
                            'meaning': value[:300],
                            'example': '',
                            'breakdown': ''
                        })
        
        # 3. Buscar en listas
        li_pattern = r'<li[^>]*>([\s\S]*?)</li>'
        for match in re.finditer(li_pattern, content, re.I):
            li_content = match.group(1)
            text = re.sub(r'<[^>]+>', ' ', li_content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            if ':' in text and len(text) > 15:
                parts = text.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if len(key) > 2 and len(value) > 3:
                        lessons.append({
                            'root': key[:80],
                            'meaning': value[:300],
                            'example': '',
                            'breakdown': ''
                        })
        
        return lessons

    def extract_lesson_from_item(self, item):
        """Extrae una lección de un item"""
        if not isinstance(item, dict):
            return None
        
        root = (item.get('root') or item.get('raiz') or item.get('title') or 
                item.get('título') or item.get('name') or item.get('tecnica') or item.get('técnica') or '')
        meaning = (item.get('meaning') or item.get('significado') or 
                   item.get('descripcion') or item.get('description') or 
                   item.get('definicion') or item.get('definition') or '')
        
        if root and meaning and len(root) > 2 and len(meaning) > 2:
            return {
                'root': str(root)[:100],
                'meaning': str(meaning)[:500],
                'example': str(item.get('example', item.get('ejemplo', '')))[:500],
                'breakdown': str(item.get('breakdown', item.get('desglose', '')))[:500]
            }
        return None

    def save_lessons(self, lessons, course):
        saved = 0
        for data in lessons:
            if not data['root'] or not data['meaning']:
                continue
            
            # Verificar duplicados
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
