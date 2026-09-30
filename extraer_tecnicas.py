#!/usr/bin/env python
import os
import re
import json
import sqlite3

print("📚 EXTRAYENDO TÉCNICAS DE HTMLs COMO EJERCICIOS")
print("=" * 60)

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# RUTAS ACTUALIZADAS
search_paths = [
    '/workspaces/Redaccion_castellana_curso',  # Directorio actual
    '/workspaces/Redaccion_castellana_curso/ejercicios_completos-lengua-castellana',
    '/home/codespace/backup_htmls',
    '/workspaces',
]

# Verificar qué rutas existen
print("🔍 Verificando rutas...")
for path in search_paths:
    if os.path.exists(path):
        print(f"  ✅ {path}")
    else:
        print(f"  ❌ {path}")

total_tecnicas = 0
archivos_procesados = 0

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
            
            # Saltar archivos de Django
            if 'site-packages' in file_path or 'venv' in file_path:
                continue
            
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
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, script)
                    for match in matches:
                        try:
                            data_str = re.sub(r'(\w+):', r'"\1":', match)
                            data_str = re.sub(r"'", '"', data_str)
                            data = json.loads(data_str)
                            
                            tec = data.get('root') or data.get('raiz') or data.get('técnica') or data.get('title') or ''
                            defi = data.get('meaning') or data.get('significado') or data.get('descripción') or data.get('description') or ''
                            
                            if tec and defi and len(tec) > 2 and len(defi) > 2:
                                tec = re.sub(r'[^\w\sáéíóúñ\-\.\,\;]', '', tec).strip()
                                defi = re.sub(r'[^\w\sáéíóúñ\-\.\,\;]', '', defi).strip()
                                
                                if tec and defi:
                                    tecnicas.append({
                                        'tecnica': tec[:100],
                                        'definicion': defi[:300],
                                        'ejemplo': str(data.get('example', ''))[:300],
                                        'desglose': str(data.get('breakdown', ''))[:300]
                                    })
                        except:
                            pass
            
            if tecnicas:
                # Obtener curso general
                cursor.execute("SELECT id FROM core_course WHERE slug = 'general'")
                result = cursor.fetchone()
                curso_id = result[0] if result else None
                
                if not curso_id:
                    # Crear curso general si no existe
                    cursor.execute("INSERT INTO core_course (slug, name, description, icon, category, is_active) VALUES ('general', 'Técnicas Generales', 'Técnicas extraídas de HTMLs', '📚', 'general', 1)")
                    curso_id = cursor.lastrowid
                
                if curso_id:
                    guardadas = 0
                    for data in tecnicas[:20]:
                        cursor.execute("SELECT id FROM core_lesson WHERE course_id = ? AND root LIKE ?", (curso_id, data['tecnica'][:30] + '%'))
                        if cursor.fetchone():
                            continue
                        
                        cursor.execute("SELECT COUNT(*) FROM core_lesson WHERE course_id = ?", (curso_id,))
                        count = cursor.fetchone()[0]
                        
                        cursor.execute("""
                            INSERT INTO core_lesson 
                            (course_id, "order", title, root, meaning, example, breakdown, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                        """, (curso_id, count + 1, data['tecnica'][:80], data['tecnica'][:80], data['definicion'][:300], data['ejemplo'][:300] if data['ejemplo'] else '', data['desglose'][:300] if data['desglose'] else ''))
                        guardadas += 1
                    
                    if guardadas > 0:
                        total_tecnicas += guardadas
                        archivos_procesados += 1
                        print(f'  ✅ {file[:40]}: {guardadas} técnicas')

conn.commit()
conn.close()

print(f'\n{"=" * 60}')
print(f'🎉 TOTAL: {total_tecnicas} técnicas extraídas de {archivos_procesados} archivos')
