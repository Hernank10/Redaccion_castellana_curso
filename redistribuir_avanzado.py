#!/usr/bin/env python
"""
📚 REDISTRIBUIDOR AVANZADO DE LECCIONES
========================================
Mueve lecciones de "Técnicas Generales" a cursos específicos
basado en palabras clave más amplias.
"""

import sqlite3
import re

print("📚 Redistribuyendo técnicas de 'general' a cursos específicos...")
print("=" * 60)

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Obtener cursos
cursor.execute("SELECT id, slug, name FROM core_course")
cursos = cursor.fetchall()
curso_map = {row[0]: row[1] for row in cursos}

# Obtener curso general
cursor.execute("SELECT id FROM core_course WHERE slug = 'general'")
general = cursor.fetchone()
if not general:
    print("❌ Curso general no encontrado")
    exit(1)
general_id = general[0]

# Obtener lecciones de general
cursor.execute("SELECT id, root, meaning, breakdown FROM core_lesson WHERE course_id = ?", (general_id,))
lessons = cursor.fetchall()
print(f"📖 {len(lessons)} lecciones en general")

# Palabras clave por curso (más amplias)
keywords = {
    'gramatica': [
        'sustantivo', 'adjetivo', 'verbo', 'adverbio', 'preposición', 'conjunción',
        'morfología', 'sintaxis', 'gramática', 'oración', 'sujeto', 'predicado',
        'concordancia', 'flexión', 'desinencia', 'raíz', 'lexema', 'morfema',
        'género', 'número', 'persona', 'tiempo', 'modo', 'aspecto'
    ],
    'sintaxis': [
        'sintaxis', 'sintáctico', 'estructura', 'frase', 'cláusula', 'complemento',
        'objeto', 'directo', 'indirecto', 'circunstancial', 'atributo', 'oración',
        'subordinada', 'coordinada', 'yuxtapuesta', 'concordancia'
    ],
    'ortografia': [
        'ortografía', 'tilde', 'acento', 'acentuación', 'diacrítica', 'mayúscula',
        'minúscula', 'b', 'v', 'g', 'j', 'c', 's', 'z', 'h', 'll', 'y', 'r', 'rr',
        'signos', 'puntuación', 'coma', 'punto', 'guión', 'paréntesis'
    ],
    'puntuacion': [
        'puntuación', 'coma', 'punto', 'guión', 'paréntesis', 'interrogación',
        'exclamación', 'puntos suspensivos', 'dos puntos', 'punto y coma'
    ],
    'retorica': [
        'retórica', 'metáfora', 'símil', 'hipérbole', 'ironía', 'antítesis',
        'paradoja', 'oxímoron', 'personificación', 'aliteración', 'anáfora',
        'epífora', 'polisíndeton', 'asíndeton', 'figura', 'tropo'
    ],
    'narracion': [
        'narración', 'cuento', 'historia', 'relato', 'trama', 'personaje',
        'acción', 'diálogo', 'secuencia', 'tiempo', 'espacio', 'narrativa',
        'novela', 'crónica', 'fábula', 'leyenda'
    ],
    'argumentacion': [
        'argumentación', 'tesis', 'persuasión', 'razonamiento', 'evidencia',
        'prueba', 'justificar', 'demostrar', 'concluir', 'premisa',
        'silogismo', 'falacia', 'debate', 'contraargumento'
    ],
    'exposicion': [
        'exposición', 'ensayo', 'definir', 'explicar', 'aclarar', 'informar',
        'describir', 'presentar', 'detallar', 'especificar', 'expositivo'
    ],
    'descripcion': [
        'descripción', 'adjetivo', 'calificativo', 'cualidad', 'característica',
        'atributo', 'rasgo', 'propiedad', 'detalle'
    ],
    'conectores': [
        'conector', 'anáfora', 'catáfora', 'cohesión', 'coherencia', 'enlace',
        'marcador', 'aditivo', 'adversativo', 'causal', 'consecutivo'
    ],
    'fonetica': [
        'fonética', 'fonología', 'sonido', 'vocal', 'consonante', 'diptongo',
        'triptongo', 'sílaba', 'acento', 'entonación', 'AFI', 'fonema'
    ],
    'perifrasis': [
        'perífrasis', 'verbal', 'infinitivo', 'gerundio', 'participio',
        'obligación', 'posibilidad', 'tener que', 'deber', 'poder'
    ],
    'comparacion': [
        'comparación', 'comparativo', 'superlativo', 'igualdad', 'inferioridad',
        'superioridad', 'tan como', 'más que', 'menos que'
    ],
    'literatura': [
        'literatura', 'novela', 'poema', 'escritor', 'autor', 'obra', 'libro',
        'lectura', 'literario', 'narrativa', 'lírica', 'dramática'
    ],
    'poesia': [
        'poesía', 'poema', 'verso', 'estrofa', 'rima', 'métrica', 'lírica',
        'poético', 'soneto', 'haiku', 'romance'
    ],
    'etimologia': [
        'etimología', 'raíz', 'griego', 'latín', 'prefijo', 'sufijo', 'origen',
        'indoeuropeo', 'proto', 'semántica'
    ],
    'comunicacion': [
        'comunicación', 'mensaje', 'emisor', 'receptor', 'canal', 'contexto',
        'feedback', 'escucha', 'habla', 'diálogo'
    ],
    'academica': [
        'académico', 'tesis', 'investigación', 'resumen', 'abstract',
        'introducción', 'metodología', 'resultados', 'conclusiones'
    ],
    'cientifica': [
        'científico', 'experimento', 'método', 'hipótesis', 'datos',
        'análisis', 'discusión', 'bibliografía', 'IMRD', 'artículo'
    ],
}

moved = 0
total_lessons = len(lessons)

for idx, (lesson_id, root, meaning, breakdown) in enumerate(lessons, 1):
    text = (root + ' ' + meaning + ' ' + (breakdown or '')).lower()
    
    best_match = None
    best_score = 0
    
    for slug, words in keywords.items():
        score = sum(1 for word in words if word in text)
        if score > best_score:
            best_score = score
            best_match = slug
    
    if best_match and best_score >= 2:
        cursor.execute("SELECT id FROM core_course WHERE slug = ?", (best_match,))
        course = cursor.fetchone()
        if course:
            course_id = course[0]
            cursor.execute("SELECT COUNT(*) FROM core_lesson WHERE course_id = ?", (course_id,))
            count = cursor.fetchone()[0]
            cursor.execute("""
                UPDATE core_lesson SET course_id = ?, "order" = ?
                WHERE id = ?
            """, (course_id, count + 1, lesson_id))
            moved += 1
            if moved % 10 == 0:
                print(f"  📦 {moved} lecciones movidas...")

print(f"\n✅ {moved} de {total_lessons} lecciones redistribuidas")

# Reordenar todas las lecciones
print("\n🔧 Reordenando lecciones...")
for course_id, slug in curso_map.items():
    cursor.execute("SELECT id FROM core_lesson WHERE course_id = ? ORDER BY id", (course_id,))
    lessons_in_course = cursor.fetchall()
    for i, (lid,) in enumerate(lessons_in_course, 1):
        cursor.execute("UPDATE core_lesson SET \"order\" = ? WHERE id = ?", (i, lid))

conn.commit()
conn.close()

print("✅ ¡Redistribución completada!")
