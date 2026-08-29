import sqlite3

print("📚 Redistribuyendo lecciones (sin reordenar)...")
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Obtener el curso general
cursor.execute("SELECT id FROM core_course WHERE slug = 'general'")
general = cursor.fetchone()
if not general:
    print("❌ Curso general no encontrado")
    exit(1)
general_id = general[0]

# Obtener lecciones de general
cursor.execute("SELECT id, root, meaning FROM core_lesson WHERE course_id = ?", (general_id,))
lessons = cursor.fetchall()
print(f"📖 {len(lessons)} lecciones en general")

# Palabras clave por curso
keywords = {
    'gramatica': ['sustantivo', 'adjetivo', 'verbo', 'adverbio', 'preposición', 'conjunción', 'morfología', 'sintaxis', 'gramática', 'oración', 'sujeto', 'predicado', 'concordancia', 'flexión', 'desinencia', 'lexema', 'morfema'],
    'ortografia': ['ortografía', 'tilde', 'acento', 'acentuación', 'diacrítica', 'mayúscula', 'minúscula', 'b', 'v', 'g', 'j', 'c', 's', 'z', 'h', 'll', 'y', 'r', 'rr', 'coma', 'punto'],
    'retorica': ['retórica', 'metáfora', 'símil', 'hipérbole', 'ironía', 'antítesis', 'paradoja', 'oxímoron', 'personificación', 'aliteración', 'anáfora', 'figura'],
    'narracion': ['narración', 'cuento', 'historia', 'relato', 'trama', 'personaje', 'acción', 'diálogo', 'narrativa', 'novela', 'crónica', 'fábula'],
    'argumentacion': ['argumentación', 'tesis', 'persuasión', 'razonamiento', 'evidencia', 'prueba', 'justificar', 'demostrar', 'concluir', 'premisa'],
    'exposicion': ['exposición', 'ensayo', 'definir', 'explicar', 'aclarar', 'informar', 'describir', 'presentar'],
    'descripcion': ['descripción', 'adjetivo', 'calificativo', 'cualidad', 'característica', 'atributo', 'rasgo'],
    'conectores': ['conector', 'anáfora', 'catáfora', 'cohesión', 'coherencia', 'enlace', 'marcador'],
    'fonetica': ['fonética', 'fonología', 'sonido', 'vocal', 'consonante', 'diptongo', 'sílaba', 'acento', 'entonación', 'AFI', 'fonema'],
    'perifrasis': ['perífrasis', 'verbal', 'infinitivo', 'gerundio', 'participio', 'obligación', 'posibilidad', 'tener que', 'deber', 'poder'],
    'comparacion': ['comparación', 'comparativo', 'superlativo', 'igualdad', 'inferioridad', 'superioridad', 'tan como', 'más que', 'menos que'],
    'literatura': ['literatura', 'novela', 'poema', 'escritor', 'autor', 'obra', 'libro', 'lectura', 'literario', 'narrativa', 'lírica', 'dramática'],
    'poesia': ['poesía', 'poema', 'verso', 'estrofa', 'rima', 'métrica', 'lírica', 'poético', 'soneto', 'haiku', 'romance'],
    'etimologia': ['etimología', 'raíz', 'griego', 'latín', 'prefijo', 'sufijo', 'origen', 'indoeuropeo'],
    'sintaxis': ['sintaxis', 'sintáctico', 'estructura', 'frase', 'cláusula', 'complemento', 'objeto', 'directo', 'indirecto', 'circunstancial', 'atributo', 'subordinada', 'coordinada', 'yuxtapuesta'],
    'comunicacion': ['comunicación', 'mensaje', 'emisor', 'receptor', 'canal', 'contexto', 'feedback', 'escucha', 'habla', 'diálogo'],
    'academica': ['académico', 'tesis', 'investigación', 'resumen', 'abstract', 'introducción', 'metodología', 'resultados', 'conclusiones'],
    'cientifica': ['científico', 'experimento', 'método', 'hipótesis', 'datos', 'análisis', 'discusión', 'bibliografía', 'IMRD', 'artículo'],
}

moved = 0
for lesson_id, root, meaning in lessons:
    text = (root + ' ' + meaning).lower()
    best_match = None
    best_score = 0
    for slug, words in keywords.items():
        score = sum(1 for w in words if w in text)
        if score > best_score:
            best_score = score
            best_match = slug
    if best_match and best_score >= 2:
        cursor.execute("SELECT id FROM core_course WHERE slug = ?", (best_match,))
        course = cursor.fetchone()
        if course:
            course_id = course[0]
            # Usar MAX("order") con comillas dobles
            cursor.execute('SELECT MAX("order") FROM core_lesson WHERE course_id = ?', (course_id,))
            max_order = cursor.fetchone()[0]
            if max_order is None:
                max_order = 0
            else:
                max_order = int(max_order)
            cursor.execute("""
                UPDATE core_lesson SET course_id = ?, "order" = ?
                WHERE id = ?
            """, (course_id, max_order + 1, lesson_id))
            moved += 1
            if moved % 10 == 0:
                print(f"  📦 {moved} lecciones movidas...")

conn.commit()
conn.close()

print(f"✅ {moved} lecciones redistribuidas")
