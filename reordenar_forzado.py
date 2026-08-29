import sqlite3

print("🔧 Reordenando todas las lecciones sin conflictos...")
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Obtener todos los cursos
cursor.execute("SELECT id, name FROM core_course")
courses = cursor.fetchall()

for course_id, course_name in courses:
    # Paso 1: Asignar un order negativo temporal (basado en id) para evitar conflictos
    cursor.execute("UPDATE core_lesson SET \"order\" = -id WHERE course_id = ?", (course_id,))
    conn.commit()
    
    # Paso 2: Reasignar order secuencial
    cursor.execute("SELECT id FROM core_lesson WHERE course_id = ? ORDER BY id", (course_id,))
    lesson_ids = cursor.fetchall()
    for new_order, (lesson_id,) in enumerate(lesson_ids, 1):
        cursor.execute("UPDATE core_lesson SET \"order\" = ? WHERE id = ?", (new_order, lesson_id))
    conn.commit()
    
    # Verificar cuántas lecciones tiene el curso
    cursor.execute("SELECT COUNT(*) FROM core_lesson WHERE course_id = ?", (course_id,))
    count = cursor.fetchone()[0]
    print(f"✅ {course_name}: {count} lecciones reordenadas")

conn.close()
print("🎉 ¡Reordenación completada!")
