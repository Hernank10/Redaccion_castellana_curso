#!/usr/bin/env python
import os
import re
import json
import sqlite3
import random

print("📝 GENERANDO EJERCICIOS DESDE HTMLs")
print("=" * 50)

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Buscar archivos HTML
search_paths = [
    '/home/codespace/backup_htmls',
    '/workspaces/Redaccion_castellana_curso/ejercicios_completos-lengua-castellana',
]

total_exercises = 0

for base_path in search_paths:
    if not os.path.exists(base_path):
        continue
    
    print(f'\n📂 Buscando en: {base_path}')
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if not file.endswith('.html'):
                continue
            
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except:
                continue
            
            # Buscar ejercicios en scripts
            script_pattern = r'<script[^>]*>([\s\S]*?)</script>'
            scripts = re.findall(script_pattern, content)
            
            for script in scripts:
                # Buscar arrays de preguntas
                patterns = [
                    r'\{[^{}]*"question"[^{}]*"options"[^{}]*"answer"[^{}]*\}',
                    r'\{[^{}]*"pregunta"[^{}]*"opciones"[^{}]*"respuesta"[^{}]*\}',
                    r'\{[^{}]*"q"[^{}]*"opts"[^{}]*"ans"[^{}]*\}',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, script)
                    for match in matches:
                        try:
                            data_str = re.sub(r'(\w+):', r'"\1":', match)
                            data_str = re.sub(r"'", '"', data_str)
                            data = json.loads(data_str)
                            
                            question = data.get('question') or data.get('pregunta') or data.get('q') or ''
                            options = data.get('options') or data.get('opciones') or data.get('opts') or []
                            answer = data.get('answer') or data.get('respuesta') or data.get('ans') or ''
                            
                            if question and options and len(options) >= 2:
                                # Asignar a una lección aleatoria
                                cursor.execute("SELECT id FROM core_lesson ORDER BY RANDOM() LIMIT 1")
                                lesson = cursor.fetchone()
                                
                                if lesson:
                                    lesson_id = lesson[0]
                                    
                                    # Asegurar 4 opciones
                                    while len(options) < 4:
                                        options.append('Ninguna de las anteriores')
                                    
                                    # Determinar opción correcta
                                    correct = 'A'
                                    if isinstance(answer, int):
                                        correct = ['A', 'B', 'C', 'D'][answer]
                                    elif isinstance(answer, str):
                                        for i, opt in enumerate(options):
                                            if opt.lower() == answer.lower():
                                                correct = ['A', 'B', 'C', 'D'][i]
                                                break
                                    
                                    cursor.execute("""
                                        INSERT INTO core_exercise 
                                        (lesson_id, question, option_a, option_b, option_c, option_d, correct_answer)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)
                                    """, (lesson_id, question[:500], options[0][:200], options[1][:200], options[2][:200], options[3][:200], correct))
                                    
                                    total_exercises += 1
                        except:
                            pass

conn.commit()
conn.close()

print(f'\n{"=" * 50}')
print(f'🎉 TOTAL: {total_exercises} ejercicios generados')
