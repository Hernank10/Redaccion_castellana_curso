#!/usr/bin/env python
import os
import sqlite3
import sys
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def connect_db():
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    if not os.path.exists(db_path):
        print(f"{Colors.RED}❌ Base de datos no encontrada: {db_path}{Colors.END}")
        sys.exit(1)
    return sqlite3.connect(db_path)

def show_tables(cursor):
    print(f"\n{Colors.HEADER}{Colors.BOLD}📊 TABLAS EN LA BASE DE DATOS{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    for table in cursor.fetchall():
        table_name = table[0]
        if table_name.startswith('core_'):
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  📋 {Colors.GREEN}{table_name}{Colors.END}: {Colors.YELLOW}{count}{Colors.END} registros")

def show_courses(cursor):
    print(f"\n{Colors.HEADER}{Colors.BOLD}📚 CURSOS DISPONIBLES{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    cursor.execute("SELECT id, name, slug, icon, description, category, is_active FROM core_course ORDER BY id")
    for row in cursor.fetchall():
        id, name, slug, icon, description, category, is_active = row
        status = f"{Colors.GREEN}✅ activo{Colors.END}" if is_active else f"{Colors.RED}❌ inactivo{Colors.END}"
        cursor.execute("SELECT COUNT(*) FROM core_lesson WHERE course_id = ?", (id,))
        lesson_count = cursor.fetchone()[0]
        print(f"  {Colors.CYAN}{icon}{Colors.END} {Colors.BOLD}{name}{Colors.END}")
        print(f"    📌 Slug: {slug}")
        print(f"    📖 Lecciones: {Colors.YELLOW}{lesson_count}{Colors.END}")
        print(f"    📂 Categoría: {category}")
        print(f"    🔹 Estado: {status}")
        print()

def show_lessons(cursor, limit=10):
    print(f"\n{Colors.HEADER}{Colors.BOLD}📖 ÚLTIMAS LECCIONES ({limit} más recientes){Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    # Usar "order" entre comillas dobles o comillas invertidas
    cursor.execute('''
        SELECT l.id, l.title, l.root, l.meaning, c.name as course_name, l."order"
        FROM core_lesson l
        JOIN core_course c ON l.course_id = c.id
        ORDER BY l.id DESC
        LIMIT ?
    ''', (limit,))
    for row in cursor.fetchall():
        id, title, root, meaning, course_name, order = row
        print(f"  {Colors.YELLOW}#{id}{Colors.END} {Colors.CYAN}[{course_name}]{Colors.END}")
        print(f"    📝 Título: {Colors.BOLD}{title[:50]}{Colors.END}")
        print(f"    📖 Raíz: {Colors.GREEN}{root[:40]}{Colors.END}")
        meaning_short = meaning[:60] + '...' if len(meaning) > 60 else meaning
        print(f"    💡 Significado: {Colors.BLUE}{meaning_short}{Colors.END}")
        print()

def show_lesson_by_course(cursor, course_name):
    print(f"\n{Colors.HEADER}{Colors.BOLD}📖 LECCIONES DEL CURSO: {course_name}{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    cursor.execute('''
        SELECT l."order", l.title, l.root, l.meaning
        FROM core_lesson l
        JOIN core_course c ON l.course_id = c.id
        WHERE c.name LIKE ?
        ORDER BY l."order"
        LIMIT 30
    ''', (f'%{course_name}%',))
    results = cursor.fetchall()
    if not results:
        print(f"{Colors.RED}❌ Curso no encontrado: {course_name}{Colors.END}")
        return
    for order, title, root, meaning in results:
        print(f"  {Colors.YELLOW}#{order}{Colors.END} {Colors.CYAN}{title}{Colors.END}")
        print(f"    📖 Raíz: {Colors.GREEN}{root}{Colors.END}")
        print(f"    💡 {Colors.BLUE}{meaning[:80]}{Colors.END}")
        print()

def show_stats(cursor):
    print(f"\n{Colors.HEADER}{Colors.BOLD}📊 ESTADÍSTICAS GENERALES{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    cursor.execute("SELECT COUNT(*) FROM core_lesson")
    total_lessons = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM core_course WHERE is_active = 1")
    total_courses = cursor.fetchone()[0]
    print(f"  {Colors.GREEN}✅ Total lecciones:{Colors.END} {Colors.YELLOW}{total_lessons}{Colors.END}")
    print(f"  {Colors.GREEN}✅ Total cursos activos:{Colors.END} {Colors.YELLOW}{total_courses}{Colors.END}")
    print(f"\n  {Colors.BOLD}📚 Distribución:{Colors.END}")
    cursor.execute("""
        SELECT c.name, c.icon, COUNT(l.id) as count
        FROM core_course c
        LEFT JOIN core_lesson l ON l.course_id = c.id
        GROUP BY c.id
        ORDER BY count DESC
    """)
    for name, icon, count in cursor.fetchall():
        if count > 0:
            bar = '█' * min(int(count / 5), 30)
            print(f"    {icon} {name}: {Colors.YELLOW}{count}{Colors.END} {Colors.CYAN}{bar}{Colors.END}")

def search_lessons(cursor, search_term):
    print(f"\n{Colors.HEADER}{Colors.BOLD}🔍 BUSCANDO: '{search_term}'{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    cursor.execute("""
        SELECT l.title, l.root, l.meaning, c.name as course_name
        FROM core_lesson l
        JOIN core_course c ON l.course_id = c.id
        WHERE l.title LIKE ? OR l.root LIKE ? OR l.meaning LIKE ?
        LIMIT 25
    """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
    results = cursor.fetchall()
    if not results:
        print(f"{Colors.RED}❌ No se encontraron resultados para '{search_term}'{Colors.END}")
        return
    for title, root, meaning, course_name in results:
        meaning_short = meaning[:80] + '...' if len(meaning) > 80 else meaning
        print(f"  {Colors.CYAN}[{course_name}]{Colors.END} {Colors.YELLOW}{title[:40]}{Colors.END}")
        print(f"    📖 {Colors.GREEN}{root[:40]}{Colors.END}")
        print(f"    💡 {Colors.BLUE}{meaning_short}{Colors.END}")
        print()

def main():
    conn = connect_db()
    cursor = conn.cursor()
    print(f"\n{Colors.HEADER}{Colors.BOLD}⌛ ARCHIVO DE VECTOR - BASE DE DATOS{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'cursos' or command == 'courses':
            show_courses(cursor)
        elif command == 'lecciones' or command == 'lessons':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            show_lessons(cursor, limit)
        elif command == 'curso' or command == 'course':
            if len(sys.argv) > 2:
                show_lesson_by_course(cursor, sys.argv[2])
            else:
                print(f"{Colors.RED}❌ Especifica un nombre de curso: python show_db.py curso 'Narración'{Colors.END}")
        elif command == 'buscar' or command == 'search':
            if len(sys.argv) > 2:
                search_lessons(cursor, ' '.join(sys.argv[2:]))
            else:
                print(f"{Colors.RED}❌ Especifica un término de búsqueda: python show_db.py buscar 'tiempo'{Colors.END}")
        elif command == 'stats':
            show_stats(cursor)
        elif command == 'tablas' or command == 'tables':
            show_tables(cursor)
        else:
            print(f"{Colors.RED}❌ Comando desconocido: {command}{Colors.END}")
            print(f"\n{Colors.YELLOW}Comandos disponibles:{Colors.END}")
            print("  python show_db.py stats        - Estadísticas generales")
            print("  python show_db.py cursos       - Listar cursos")
            print("  python show_db.py lecciones N  - Últimas N lecciones")
            print("  python show_db.py curso NOMBRE - Lecciones de un curso")
            print("  python show_db.py buscar TEXTO - Buscar lecciones")
            print("  python show_db.py tablas       - Mostrar tablas")
    else:
        show_stats(cursor)
    conn.close()
    print(f"\n{Colors.CYAN}{'='*50}{Colors.END}")

if __name__ == "__main__":
    main()
