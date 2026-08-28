#!/usr/bin/env python
import sqlite3
import re

print("📚 Redistribuyendo lecciones de 'Técnicas Generales'...")

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Obtener el curso "Técnicas Generales"
cursor.execute("SELECT id FROM core_course WHERE slug = 'general'")
general = cursor.fetchone()

if not general:
    print("❌ Curso 'Técnicas Generales' no encontrado")
    exit(1)

general_id = general[0]

# Obtener lecciones
cursor.execute("""
    SELECT id, root, meaning, title
    FROM core_lesson
    WHERE course_id = ?
    ORDER BY id
""", (general_id,))

lessons = cursor.fetchall()
print(f"📖 {len(lessons)} lecciones en Técnicas Generales")

# Mapeo de palabras clave a cursos
keyword_map = {
    'gramatica': ['gramática', 'gramatica', 'regla', 'norma', 'RAE', 'morfología', 'flexión', 'categoría'],
    'sintaxis': ['sintaxis', 'sintáctico', 'orden', 'estructura', 'frase', 'oración', 'complemento', 'sujeto', 'predicado'],
    'literatura': ['literatura', 'novela', 'cuento', 'poema', 'escritor', 'autor', 'obra', 'libro', 'narrativa'],
    'poesia': ['poesía', 'poema', 'verso', 'estrofa', 'rima', 'métrica', 'poético', 'lírica'],
    'ortografia': ['ortografía', 'tildes', 'acentos', 'mayúsculas', 'minúsculas', 'tilde', 'diacrítica'],
    'redaccion_avanzada': ['redacción', 'estilo', 'párrafo', 'texto', 'escribir', 'composición', 'coherencia'],
    'comunicacion': ['comunicación', 'mensaje', 'emisor', 'receptor', 'canal', 'contexto', 'feedback'],
    'academica': ['académico', 'tesis', 'ensayo', 'investigación', 'resumen', 'abstract', 'citación'],
    'cientifica': ['científico', 'experimento', 'método', 'hipótesis', 'resultados', 'conclusión', 'datos'],
    'periodistica': ['periodístico', 'noticia', 'reportaje', 'entrevista', 'crónica', 'editorial', 'titular'],
    'etimologia': ['raíz', 'etimología', 'griego', 'latín', 'prefijo', 'sufijo', 'origen'],
    'narracion': ['narración', 'cuento', 'historia', 'relato', 'trama', 'personaje', 'acción'],
    'argumentacion': ['argumentación', 'tesis', 'persuadir', 'razonamiento', 'evidencia', 'lógica'],
    'exposicion': ['exposición', 'explicar', 'definir', 'aclarar', 'informar'],
    'retorica': ['retórica', 'metáfora', 'símil', 'figura', 'hipérbole', 'ironía'],
    'descripcion': ['descripción', 'adjetivo', 'cualidad', 'característica'],
    'conectores': ['conector', 'anáfora', 'cohesión', 'enlace', 'transición'],
    'puntuacion': ['puntuación', 'coma', 'punto', 'signo', 'paréntesis', 'guión'],
    'fonetica': ['fonética', 'sonido', 'vocal', 'consonante', 'AFI', 'pronunciación'],
    'perifrasis': ['perífrasis', 'verbo', 'infinitivo', 'gerundio', 'participio'],
    'comparacion': ['comparación', 'comparativo', 'superlativo', 'igualdad', 'superioridad'],
}

moved = 0

for lesson_id, root, meaning, title in lessons:
    text = (root + ' ' + meaning + ' ' + title).lower()
    
    best_match = None
    best_score = 0
    
    for slug, keywords in keyword_map.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_match = slug
    
    if best_match and best_score >= 1:
        cursor.execute("SELECT id FROM core_course WHERE slug = ?", (best_match,))
        course = cursor.fetchone()
        
        if course:
            course_id = course[0]
            cursor.execute("SELECT MAX('order') FROM core_lesson WHERE course_id = ?", (course_id,))
            last_order = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                UPDATE core_lesson 
                SET course_id = ?, "order" = ?
                WHERE id = ?
            """, (course_id, last_order + 1, lesson_id))
            moved += 1
            if moved % 10 == 0:
                print(f"  ✅ {moved} lecciones redistribuidas")

conn.commit()
conn.close()

print(f"\n🎉 {moved} lecciones redistribuidas de Técnicas Generales")
