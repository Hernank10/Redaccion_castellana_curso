#!/usr/bin/env python
import os
import re
import json
import sqlite3

print("📚 EXTRAYENDO TÉCNICAS DE HTMLs COMO EJERCICIOS")
print("=" * 60)

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

search_paths = [
    '/home/codespace/backup_htmls',
    '/workspaces/Redaccion_castellana_curso/ejercicios_completos-lengua-castellana',
]

total_tecnicas = 0
archivos_procesados = 0

category_map = {
    'etimologia': ['etimologia', 'raiz', 'grecolatinas', 'prefijo', 'sufijo'],
    'narracion': ['narracion', 'cuento', 'historia', 'relato', 'fabula'],
    'retorica': ['retorica', 'figura', 'metafora', 'simil', 'alegoria'],
    'gramatica': ['gramatica', 'sintaxis', 'morfologia', 'oracion'],
    'puntuacion': ['puntuacion', 'ortografia', 'signos', 'coma', 'tilde'],
    'conectores': ['conector', 'cohesion', 'anfora', 'catafora'],
    'argumentacion': ['argumentacion', 'tesis', 'persuasion', 'evidencia'],
    'descripcion': ['descripcion', 'adjetivo', 'calificativo', 'sensorial'],
    'exposicion': ['exposicion', 'ensayo', 'definir', 'explicar'],
    'comparacion': ['comparacion', 'comparativo', 'superlativo'],
    'fonetica': ['fonetica', 'sonido', 'vocal', 'consonante'],
    'perifrasis': ['perifrasis', 'verbal', 'infinitivo', 'gerundio'],
    'literatura': ['literatura', 'novela', 'poema', 'escritor'],
    'poesia': ['poesia', 'poema', 'verso', 'estrofa'],
}

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
            
            categoria = 'general'
            for cat, keywords in category_map.items():
                for keyword in keywords:
                    if keyword in file_lower:
                        categoria = cat
                        break
                if categoria != 'general':
                    break
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except:
                continue
            
            tecnicas = []
            
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
                    r'\{[^{}]*"tecnica"[^{}]*"definicion"[^{}]*\}',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, script)
                    for match in matches:
                        try:
                            data_str = re.sub(r'(\w+):', r'"\1":', match)
                            data_str = re.sub(r"'", '"', data_str)
                            data = json.loads(data_str)
                            
                            tec = data.get('root') or data.get('raiz') or data.get('técnica') or data.get('tecnica') or data.get('title') or data.get('name') or ''
                            defi = data.get('meaning') or data.get('significado') or data.get('descripción') or data.get('description') or data.get('desc') or data.get('definicion') or ''
                            
                            if tec and defi and len(tec) > 2 and len(defi) > 2:
                                tec = re.sub(r'[^\w\sáéíóúñ\-\.\,\;]', '', tec).strip()
                                defi = re.sub(r'[^\w\sáéíóúñ\-\.\,\;]', '', defi).strip()
                                
                                if tec and defi:
                                    tecnicas.append({
                                        'tecnica': tec[:100],
                                        'definicion': defi[:300],
                                        'ejemplo': str(data.get('example', data.get('ejemplo', '')))[:300],
                                        'desglose': str(data.get('breakdown', data.get('desglose', '')))[:300]
                                    })
                        except:
                            pass
            
            # Buscar en divs
            if not tecnicas:
                div_pattern = r'<div[^>]*class="[^"]*(?:tecnica|técnica|card|item|lesson)[^"]*"[^>]*>([\s\S]*?)</div>'
                for match in re.finditer(div_pattern, content, re.I):
                    div_content = match.group(1)
                    text = re.sub(r'<[^>]+>', ' ', div_content)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if ':' in text and len(text) > 20:
                        parts = text.split(':', 1)
                        if len(parts) == 2:
                            tec = parts[0].strip()
                            defi = parts[1].strip()
                            if len(tec) > 2 and len(defi) > 5 and len(tec) < 100:
                                tecnicas.append({
                                    'tecnica': tec[:80],
                                    'definicion': defi[:300],
                                    'ejemplo': '',
                                    'desglose': ''
                                })
            
            if tecnicas:
                curso_id = None
                for cat, keywords in category_map.items():
                    for keyword in keywords:
                        if keyword in file_lower:
                            cursor.execute("SELECT id FROM core_course WHERE slug = ?", (cat,))
                            result = cursor.fetchone()
                            if result:
                                curso_id = result[0]
                                break
                            break
                    if curso_id:
                        break
                
                if not curso_id:
                    cursor.execute("SELECT id FROM core_course WHERE slug = 'general'")
                    result = cursor.fetchone()
                    curso_id = result[0] if result else None
                
                if curso_id:
                    guardadas = 0
                    for data in tecnicas[:20]:
                        cursor.execute("SELECT id FROM core_lesson WHERE course_id = ? AND root LIKE ?", (curso_id, data['tecnica'][:30] + '%'))
                        if cursor.fetchone():
                            continue
                        
                        # Obtener último order - CORREGIDO
                        cursor.execute("SELECT COUNT(*) FROM core_lesson WHERE course_id = ?", (curso_id,))
                        count = cursor.fetchone()[0]
                        last_order = count
                        
                        cursor.execute("""
                            INSERT INTO core_lesson 
                            (course_id, "order", title, root, meaning, example, breakdown, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                        """, (curso_id, last_order + 1, data['tecnica'][:80], data['tecnica'][:80], data['definicion'][:300], data['ejemplo'][:300] if data['ejemplo'] else '', data['desglose'][:300] if data['desglose'] else ''))
                        guardadas += 1
                    
                    if guardadas > 0:
                        total_tecnicas += guardadas
                        archivos_procesados += 1
                        print(f'  ✅ {file[:40]}: {guardadas} técnicas → {categoria}')

conn.commit()
conn.close()

print(f'\n{"=" * 60}')
print(f'🎉 TOTAL: {total_tecnicas} técnicas extraídas de {archivos_procesados} archivos')
