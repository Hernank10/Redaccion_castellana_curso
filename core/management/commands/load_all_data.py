import os
import json
import re
from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Extrae y carga todas las técnicas de todos los archivos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 INICIANDO EXTRACCIÓN MASIVA...'))
        
        # Crear cursos base
        self.create_courses()
        
        # Buscar archivos
        search_paths = [
            '/workspaces/Redaccion_castellana_curso/ejercicios_completos-lengua-castellana',
            '/workspaces/Redaccion_castellana_curso',
            '/home/codespace/backup_htmls',
        ]
        
        total_lessons = 0
        files_processed = 0
        
        for base_path in search_paths:
            if not os.path.exists(base_path):
                continue
            self.stdout.write(f'📂 Buscando en: {base_path}')
            
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.startswith('.'):
                        continue
                    file_path = os.path.join(root, file)
                    
                    if file.endswith('.html'):
                        lessons = self.extract_from_html(file_path)
                    elif file.endswith('.json'):
                        lessons = self.extract_from_json(file_path)
                    elif file.endswith('.txt') or file.endswith('.md'):
                        lessons = self.extract_from_text(file_path)
                    else:
                        continue
                    
                    if lessons:
                        files_processed += 1
                        saved = self.save_lessons(lessons, file_path)
                        total_lessons += saved
                        self.stdout.write(f'  ✅ {os.path.basename(file_path)} → {saved} lecciones')
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 COMPLETADO: {total_lessons} lecciones de {files_processed} archivos'))

    def create_courses(self):
        courses = [
            ('etimologia', 'Raíces y Etimología', '📜', 'etymology'),
            ('perifrasis', 'Perífrasis Verbales', '⚡', 'periphrasis'),
            ('fonetica', 'Fonética y AFI', '🔊', 'phonetics'),
            ('puntuacion', 'Signos de Puntuación', '✍️', 'punctuation'),
            ('conectores', 'Conectores y Cohesión', '🔗', 'connectors'),
            ('retorica', 'Figuras Retóricas', '🎭', 'rhetoric'),
            ('comparacion', 'Fórmulas de Comparación', '⚖️', 'comparison'),
            ('descripcion', 'Fórmulas de Descripción', '🖌️', 'description'),
            ('exposicion', 'Fórmulas de Exposición', '📊', 'exposition'),
            ('argumentacion', 'Fórmulas de Argumentación', '⚡', 'argumentation'),
            ('narracion', 'Fórmulas de Narración', '📖', 'narration'),
        ]
        for slug, name, icon, cat in courses:
            Course.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': f'100 técnicas de {name}', 'icon': icon, 'category': cat}
            )
        Course.objects.get_or_create(
            slug='general',
            defaults={'name': 'Técnicas Generales', 'description': 'Técnicas varias', 'icon': '📚', 'category': 'general'}
        )
        self.stdout.write(self.style.SUCCESS('✅ Cursos creados'))

    def extract_from_html(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return []
        
        lessons = []
        script_pattern = r'<script[^>]*>([\s\S]*?)</script>'
        scripts = re.findall(script_pattern, content)
        
        for script in scripts:
            patterns = [
                r'\{[^{}]*"root"[^{}]*"meaning"[^{}]*\}',
                r'\{[^{}]*"raiz"[^{}]*"significado"[^{}]*\}',
            ]
            for pattern in patterns:
                for match in re.finditer(pattern, script):
                    try:
                        data_str = match.group()
                        data_str = re.sub(r'(\w+):', r'"\1":', data_str)
                        data_str = re.sub(r"'", '"', data_str)
                        data = json.loads(data_str)
                        lesson = self.normalize_lesson(data)
                        if lesson:
                            lessons.append(lesson)
                    except:
                        pass
        return lessons

    def extract_from_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
        except:
            return []
        
        lessons = []
        if isinstance(data, list):
            for item in data:
                lesson = self.normalize_lesson(item)
                if lesson:
                    lessons.append(lesson)
        elif isinstance(data, dict):
            for key in ['items', 'lessons', 'lecciones', 'técnicas']:
                if key in data and isinstance(data[key], list):
                    for item in data[key]:
                        lesson = self.normalize_lesson(item)
                        if lesson:
                            lessons.append(lesson)
                    break
        return lessons

    def extract_from_text(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return []
        
        lessons = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            match = re.match(r'^([^:.-]+)[:.-]\s*(.+)$', line)
            if match:
                key = match.group(1).strip()
                val = match.group(2).strip()
                if len(key) > 1 and len(val) > 1 and len(key) < 100:
                    lessons.append({'root': key[:50], 'meaning': val[:200], 'example': '', 'breakdown': ''})
        return lessons

    def normalize_lesson(self, data):
        if not isinstance(data, dict):
            return None
        root = data.get('root') or data.get('raiz') or data.get('title') or ''
        meaning = data.get('meaning') or data.get('significado') or data.get('descripcion') or ''
        if not root or not meaning:
            return None
        return {
            'root': str(root)[:100],
            'meaning': str(meaning)[:500],
            'example': str(data.get('example', ''))[:500],
            'breakdown': str(data.get('breakdown', ''))[:500]
        }

    def save_lessons(self, lessons, file_path):
        saved = 0
        file_name = os.path.basename(file_path).lower()
        
        slug = 'general'
        for key in ['etimologia', 'perifrasis', 'fonetica', 'puntuacion', 'conectores', 'retorica', 'comparacion', 'descripcion', 'exposicion', 'argumentacion', 'narracion']:
            if key in file_name:
                slug = key
                break
        
        try:
            course = Course.objects.get(slug=slug)
        except:
            course = Course.objects.get(slug='general')
        
        for lesson_data in lessons:
            if not lesson_data:
                continue
            count = Lesson.objects.filter(course=course).count()
            Lesson.objects.create(
                course=course,
                order=count + 1,
                title=lesson_data['root'][:100],
                root=lesson_data['root'][:100],
                meaning=lesson_data['meaning'][:500],
                example=lesson_data['example'][:500] if lesson_data['example'] else '',
                breakdown=lesson_data['breakdown'][:500] if lesson_data['breakdown'] else '',
                is_active=True
            )
            saved += 1
        return saved
