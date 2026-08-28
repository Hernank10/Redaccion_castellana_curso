#!/usr/bin/env python
import sqlite3

print("📚 Distribuyendo lecciones de 'Técnicas Generales'...")

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Obtener el curso "Técnicas Generales"
cursor.execute("SELECT id FROM core_course WHERE slug = 'general'")
general_id = cursor.fetchone()

if not general_id:
    print("❌ Curso 'Técnicas Generales' no encontrado")
    exit(1)

general_id = general_id[0]

# Obtener lecciones de Técnicas Generales
cursor.execute("""
    SELECT id, root, meaning, title
    FROM core_lesson
    WHERE course_id = ?
    ORDER BY id
""", (general_id,))

lessons = cursor.fetchall()
print(f"📖 {len(lessons)} lecciones en Técnicas Generales")

# Mapeo de palabras clave
keyword_map = {
    'etimologia': ['raíz', 'raiz', 'etimología', 'etimologia', 'griego', 'latín', 'prefijo', 'sufijo'],
    'narracion': ['narración', 'cuento', 'historia', 'relato', 'narrar', 'trama', 'personaje'],
    'argumentacion': ['argumentación', 'argumento', 'tesis', 'persuadir', 'razonamiento'],
    'exposicion': ['exposición', 'explicar', 'definir', 'aclarar', 'ensayo'],
    'retorica': ['retórica', 'metáfora', 'símil', 'hipérbole', 'ironía', 'figura'],
    'descripcion': ['descripción', 'adjetivo', 'calificativo', 'cualidad'],
    'conectores': ['conector', 'anáfora', 'catáfora', 'cohesión', 'enlace'],
    'puntuacion': ['puntuación', 'coma', 'punto', 'signo', 'paréntesis'],
    'fonetica': ['fonética', 'sonido', 'vocal', 'consonante', 'AFI'],
    'perifrasis': ['perífrasis', 'verbo', 'infinitivo', 'gerundio'],
    'comparacion': ['comparación', 'comparativo', 'superlativo', 'igualdad'],
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
        course_id = cursor.fetchone()
        
        if course_id:
            course_id = course_id[0]
            # Obtener el último order del curso destino
            cursor.execute("SELECT MAX('order') FROM core_lesson WHERE course_id = ?", (course_id,))
            last_order = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                UPDATE core_lesson 
                SET course_id = ?, "order" = ?
                WHERE id = ?
            """, (course_id, last_order + 1, lesson_id))
            moved += 1
            print(f"  ✅ '{root[:30]}' → {best_match}")

conn.commit()
conn.close()

print(f"\n🎉 {moved} lecciones redistribuidas")
