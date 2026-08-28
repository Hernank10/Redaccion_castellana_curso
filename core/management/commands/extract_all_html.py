import os
import json
import re
from django.core.management.base import BaseCommand
from core.models import Course, Lesson

class Command(BaseCommand):
    help = 'Extrae datos de TODOS los archivos HTML'

    def handle(self, *args, **options):
        self.stdout.write('📂 Extrayendo datos de archivos HTML...')
        
        search_paths = [
            '/workspaces/Redaccion_castellana_curso',
            '/workspaces/Redaccion_castellana_curso/ejercicios_completos-lengua-castellana',
            '/home/codespace/backup_htmls',
        ]
        
        total = 0
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
                    lessons = self.extract_from_html(file_path)
                    
                    if lessons:
                        files_processed += 1
                        saved = self.save_lessons(lessons, file_path)
                        total += saved
                        self.stdout.write(f'  ✅ {file}: {saved} lecciones')
        
        self.stdout.write(self.style.SUCCESS(f'🎉 Total: {total} lecciones extraídas de {files_processed} archivos'))

    def extract_from_html(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return []
        
        lessons = []
        
        # Extraer patrones de datos estructurados
        patterns = [
            r'<div[^>]*class="[^"]*(?:tecnica|técnica|lesson|leccion|card|flashcard)[^"]*"[^>]*>([\s\S]*?)</div>',
            r'<script[^>]*>([\s\S]*?)</script>',
            r'<p[^>]*>([\s\S]*?)</p>',
            r'<li[^>]*>([\s\S]*?)</li>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.I)
            for match in matches:
                text = re.sub(r'<[^>]+>', ' ', match)
                text = re.sub(r'\s+', ' ', text).strip()
                
                if ':' in text and len(text) > 20:
                    parts = text.split(':')
                    if len(parts) >= 2:
                        key = parts[0].strip()
                        value = ':'.join(parts[1:]).strip()
                        if len(key) > 2 and len(value) > 5:
                            lessons.append({
                                'root': key[:80],
                                'meaning': value[:300],
                                'example': '',
                                'breakdown': ''
                            })
                
                elif ' - ' in text and len(text) > 20:
                    parts = text.split(' - ')
                    if len(parts) >= 2:
                        key = parts[0].strip()
                        value = ' - '.join(parts[1:]).strip()
                        if len(key) > 2 and len(value) > 5:
                            lessons.append({
                                'root': key[:80],
                                'meaning': value[:300],
                                'example': '',
                                'breakdown': ''
                            })
        
        # Deduplicar
        seen = set()
        unique_lessons = []
        for l in lessons:
            key = l['root'][:30]
            if key not in seen:
                seen.add(key)
                unique_lessons.append(l)
        
        return unique_lessons[:100]

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
            
            # Verificar si ya existe en este curso
            if Lesson.objects.filter(course=course, root__iexact=data['root'][:50]).exists():
                continue
            
            # Obtener el último order
            last_order = Lesson.objects.filter(course=course).order_by('-order').first()
            next_order = (last_order.order + 1) if last_order else 1
            
            Lesson.objects.create(
                course=course,
                order=next_order,
                title=data['root'][:80],
                root=data['root'][:80],
                meaning=data['meaning'][:300],
                example=data['example'][:300] if data['example'] else '',
                breakdown=data['breakdown'][:300] if data['breakdown'] else '',
                is_active=True
            )
            saved += 1
        
        return saved
