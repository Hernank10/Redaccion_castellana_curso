#!/usr/bin/env python
import os
import re
import json
import sqlite3

print("📚 EXTRAYENDO CONTENIDO REAL DE LOS HTMLs")
print("=" * 50)

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

category_map = {
    'etimologia': ['etimologia', 'raiz', 'grecolatinas', 'prefijo', 'sufijo'],
    'narracion': ['narracion', 'cuento', 'historia', 'relato', 'fabula', 'epica'],
    'retorica': ['retorica', 'figura', 'metafora', 'simil', 'alegoria', 'oximoron'],
    'gramatica': ['gramatica', 'sintaxis', 'morfologia', 'morfosintaxis', 'oracion'],
    'puntuacion': ['puntuacion', 'ortografia', 'signos', 'coma', 'tilde'],
    'conectores': ['conector', 'cohesion', 'anfora', 'catafora', 'discurso'],
    'exposicion': ['exposicion', 'ensayo', 'definir', 'explicar'],
    'argumentacion': ['argumentacion', 'tesis', 'persuasion', 'razonamiento'],
    'descripcion': ['descripcion', 'adjetivo', 'calificativo', 'sensorial'],
    'comparacion': ['comparacion', 'comparativo', 'superlativo'],
    'fonetica': ['fonetica', 'sonido', 'vocal', 'consonante', 'afi'],
    'perifrasis': ['perifrasis', 'verbal', 'infinitivo', 'gerundio'],
    'poesia': ['poesia', 'poema', 'verso', 'estrofa', 'rima'],
    'literatura': ['literatura', 'novela', 'cuento', 'poema', 'escritor'],
    'comunicacion': ['comunicacion', 'mensaje', 'emisor', 'receptor'],
    'academica': ['academica', 'tesis', 'ensayo', 'investigacion'],
    'cientifica': ['cientifica', 'experimento', 'metodo', 'hipotesis'],
    'periodistica': ['periodistica', 'noticia', 'reportaje', 'entrevista'],
}

search_paths = [
    '/home/codespace/backup_htmls',
    '/workspaces/Redaccion_castellana_curso/ejercicios_completos-lengua-castellana',
]

total_lessons = 0
files_processed = 0

for base_path in search_paths:
    if not os.path.exists(base_path):
        continue
    
    print(f'\n📂 Buscando en: {base_path}')
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if not file.endswith('.html'):
                continue
            
            file_path = os.path.join(root, file)
            file_lower = file.lower()
            
            category = None
            for cat, keywords in category_map.items():
                for keyword in keywords:
                    if keyword in file_lower:
                        category = cat
                        break
                if category:
                    break
            
            if not category:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except:
                continue
            
            lessons = []
            
            # Buscar en scripts
            script_pattern = r'<script[^>]*>([\s\S]*?)</script>'
            scripts = re.findall(script_pattern, content)
            
            for script in scripts:
                patterns = [
                    r'\{[^{}]*"root"[^{}]*"meaning"[^{}]*\}',
                    r'\{[^{}]*"raiz"[^{}]*"significado"[^{}]*\}',
                    r'\{[^{}]*"técnica"[^{}]*"descripción"[^{}]*\}',
                    r'\{[^{}]*"title"[^{}]*"description"[^{}]*\}',
                    r'\{[^{}]*"name"[^{}]*"desc"[^{}]*\}',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, script)
                    for match in matches:
                        try:
                            data_str = re.sub(r'(\w+):', r'"\1":', match)
                            data_str = re.sub(r"'", '"', data_str)
                            data = json.loads(data_str)
                            
                            root = data.get('root') or data.get('raiz') or data.get('técnica') or data.get('title') or data.get('name') or ''
                            meaning = data.get('meaning') or data.get('significado') or data.get('descripción') or data.get('description') or data.get('desc') or ''
                            
                            if root and meaning and len(root) > 2 and len(meaning) > 2:
                                root = re.sub(r'[^\w\sáéíóúñ\-\.\,\;]', '', root).strip()
                                meaning = re.sub(r'[^\w\sáéíóúñ\-\.\,\;]', '', meaning).strip()
                                
                                if root and meaning:
                                    lessons.append({
                                        'root': root[:100],
                                        'meaning': meaning[:500],
                                        'example': str(data.get('example', data.get('ejemplo', '')))[:500],
                                        'breakdown': str(data.get('breakdown', data.get('desglose', '')))[:500]
                                    })
                        except:
                            pass
            
            # Buscar en divs
            if not lessons:
                div_pattern = r'<div[^>]*class="[^"]*(?:tecnica|técnica|lesson|leccion|card|item)[^"]*"[^>]*>([\s\S]*?)</div>'
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
            
            if lessons:
                cursor.execute("SELECT id FROM core_course WHERE slug = ?", (category,))
                course = cursor.fetchone()
                
                if course:
                    course_id = course[0]
                    saved = 0
                    
                    for data in lessons:
                        cursor.execute("SELECT id FROM core_lesson WHERE course_id = ? AND root LIKE ?", (course_id, data['root'][:30] + '%'))
                        if cursor.fetchone():
                            continue
                        
                        # Obtener último order - CORREGIDO CON int()
                        cursor.execute("SELECT MAX('order') FROM core_lesson WHERE course_id = ?", (course_id,))
                        result = cursor.fetchone()[0]
                        last_order = int(result) if result is not None else 0
                        
                        cursor.execute("""
                            INSERT INTO core_lesson 
                            (course_id, "order", title, root, meaning, example, breakdown, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                        """, (course_id, last_order + 1, data['root'][:80], data['root'][:80], data['meaning'][:300], data['example'][:300] if data['example'] else '', data['breakdown'][:300] if data['breakdown'] else ''))
                        saved += 1
                    
                    if saved > 0:
                        total_lessons += saved
                        files_processed += 1
                        print(f'  ✅ {file[:40]}: {saved} lecciones → {category}')

conn.commit()
conn.close()

print(f'\n{"=" * 50}')
print(f'🎉 TOTAL: {total_lessons} lecciones extraídas de {files_processed} archivos')
