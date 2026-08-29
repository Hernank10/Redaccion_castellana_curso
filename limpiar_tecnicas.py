#!/usr/bin/env python
"""
🧹 LIMPIADOR DE LECCIONES CORRUPTAS
====================================
Elimina lecciones que contienen código HTML/CSS/JS o plantillas Django.
"""

import sqlite3
import re

print("🧹 Limpiando lecciones corruptas...")
print("=" * 60)

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Patrones de corrupción
corrupt_patterns = [
    r'\$\{',           # JavaScript ${}
    r'{% for',         # Plantillas Django
    r'{% if',          # Plantillas Django
    r'{{',             # Plantillas Django
    r'</div>',         # HTML
    r'<script',        # JavaScript
    r'<style',         # CSS
    r'body {',         # CSS
    r'padding:',       # CSS
    r'font-family',    # CSS
    r'var ',           # JavaScript
    r'let ',           # JavaScript
    r'const ',         # JavaScript
    r'function',       # JavaScript
    r'return ',        # JavaScript
    r'#\${',           # JavaScript
    r'new ',           # JavaScript
    r'this.',          # JavaScript
]

# Obtener todas las lecciones
cursor.execute("SELECT id, root, meaning, course_id FROM core_lesson")
lessons = cursor.fetchall()

deleted = 0
kept = 0

for lesson_id, root, meaning, course_id in lessons:
    text = (root + ' ' + (meaning or '')).lower()
    
    # Verificar si es corrupta
    is_corrupt = False
    for pattern in corrupt_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            is_corrupt = True
            break
    
    # Si es corrupta, eliminar
    if is_corrupt:
        cursor.execute("DELETE FROM core_lesson WHERE id = ?", (lesson_id,))
        deleted += 1
    else:
        kept += 1

conn.commit()
conn.close()

print(f"✅ Eliminadas: {deleted} lecciones corruptas")
print(f"📚 Conservadas: {kept} lecciones útiles")
