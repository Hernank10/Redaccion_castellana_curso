#!/usr/bin/env python
import sqlite3
import random
import os
import sys

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def get_courses(cursor):
    cursor.execute("""
        SELECT c.id, c.name, c.icon, COUNT(l.id) as count
        FROM core_course c
        LEFT JOIN core_lesson l ON l.course_id = c.id
        GROUP BY c.id
        HAVING count > 0
        ORDER BY count DESC
    """)
    return cursor.fetchall()

def get_lessons(cursor, course_id, limit=10):
    cursor.execute("""
        SELECT id, root, meaning, title
        FROM core_lesson
        WHERE course_id = ?
        ORDER BY RANDOM()
        LIMIT ?
    """, (course_id, limit))
    return cursor.fetchall()

def practice_mode(cursor):
    print(f"\n{Colors.HEADER}{Colors.BOLD}🎯 MODO PRÁCTICA - ARCHIVO DE VECTOR{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    
    courses = get_courses(cursor)
    
    if not courses:
        print(f"{Colors.RED}❌ No hay cursos con lecciones{Colors.END}")
        return
    
    print("\n📚 CURSOS DISPONIBLES:")
    for i, (id, name, icon, count) in enumerate(courses, 1):
        print(f"  {i}. {icon} {Colors.BOLD}{name}{Colors.END} ({Colors.YELLOW}{count}{Colors.END} lecciones)")
    
    print(f"  {len(courses)+1}. {Colors.CYAN}🎯 TODOS LOS CURSOS (mezclado){Colors.END}")
    
    # Seleccionar curso
    while True:
        try:
            choice = input(f"\n{Colors.YELLOW}Selecciona un curso (1-{len(courses)+1}): {Colors.END}")
            choice = int(choice)
            if 1 <= choice <= len(courses) + 1:
                break
        except:
            pass
        print(f"{Colors.RED}❌ Selección inválida{Colors.END}")
    
    # Seleccionar cantidad
    while True:
        try:
            limit_input = input(f"{Colors.YELLOW}¿Cuántas preguntas? (5-50, Enter=10): {Colors.END}")
            if not limit_input:
                limit = 10
                break
            limit = int(limit_input)
            if 5 <= limit <= 50:
                break
        except:
            pass
        print(f"{Colors.RED}❌ Ingresa un número entre 5 y 50{Colors.END}")
    
    # Obtener lecciones
    if choice == len(courses) + 1:
        # Todos los cursos
        all_lessons = []
        for course_id, name, icon, count in courses:
            all_lessons.extend(get_lessons(cursor, course_id, min(limit, count)))
        random.shuffle(all_lessons)
        lessons = all_lessons[:limit]
        course_name = "TODOS LOS CURSOS"
    else:
        course_id = courses[choice-1][0]
        course_name = courses[choice-1][1]
        lessons = get_lessons(cursor, course_id, limit)
    
    if not lessons:
        print(f"{Colors.RED}❌ No hay lecciones en este curso{Colors.END}")
        return
    
    print(f"\n{Colors.GREEN}🎯 Comenzando práctica de {course_name}{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}\n")
    
    score = 0
    total = len(lessons)
    
    for i, (lesson_id, root, meaning, title) in enumerate(lessons, 1):
        print(f"{Colors.YELLOW}Pregunta {i}/{total}{Colors.END}")
        print(f"📖 {Colors.CYAN}{root}{Colors.END}")
        print(f"💡 ¿Cuál es el significado de '{root[:50]}'?")
        
        # Obtener opciones incorrectas
        cursor.execute("""
            SELECT meaning FROM core_lesson
            WHERE course_id = (SELECT course_id FROM core_lesson WHERE id = ?)
            AND id != ?
            ORDER BY RANDOM()
            LIMIT 3
        """, (lesson_id, lesson_id))
        wrongs = [row[0] for row in cursor.fetchall()]
        
        while len(wrongs) < 3:
            wrongs.append("Significado desconocido")
        
        options = [meaning] + wrongs[:3]
        random.shuffle(options)
        
        for j, opt in enumerate(options, 1):
            opt_short = opt[:60] + '...' if len(opt) > 60 else opt
            print(f"  {j}. {Colors.BLUE}{opt_short}{Colors.END}")
        
        while True:
            try:
                answer = input(f"\n{Colors.YELLOW}Tu respuesta (1-4): {Colors.END}")
                answer = int(answer)
                if 1 <= answer <= 4:
                    break
            except:
                pass
            print(f"{Colors.RED}❌ Respuesta inválida (1-4){Colors.END}")
        
        if options[answer-1] == meaning:
            print(f"{Colors.GREEN}✅ ¡Correcto! 🎉{Colors.END}")
            score += 1
        else:
            print(f"{Colors.RED}❌ Incorrecto.{Colors.END}")
            print(f"  La respuesta correcta era: {Colors.GREEN}{meaning}{Colors.END}")
        
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}\n")
    
    # Resultados
    pct = round(score / total * 100, 1)
    print(f"\n{Colors.HEADER}{Colors.BOLD}📊 RESULTADOS{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    print(f"  ✅ Correctas: {Colors.GREEN}{score}{Colors.END}")
    print(f"  ❌ Incorrectas: {Colors.RED}{total - score}{Colors.END}")
    print(f"  📊 Porcentaje: {Colors.YELLOW}{pct}%{Colors.END}")
    
    if pct >= 90:
        print(f"  🌟 {Colors.GREEN}¡Excelente! Eres un maestro del Archivo de Vector.{Colors.END}")
    elif pct >= 70:
        print(f"  🌟 {Colors.CYAN}¡Bien hecho! Sigue practicando.{Colors.END}")
    else:
        print(f"  📚 {Colors.YELLOW}Sigue practicando para mejorar. ¡Tú puedes!{Colors.END}")

def main():
    db_path = 'db.sqlite3'
    if not os.path.exists(db_path):
        print(f"{Colors.RED}❌ Base de datos no encontrada{Colors.END}")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    practice_mode(cursor)
    
    conn.close()

if __name__ == "__main__":
    main()
