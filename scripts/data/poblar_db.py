#!/usr/bin/env python
"""
📦 POBLADOR AUTOMÁTICO DEL ARCHIVO DE VECTOR
============================================
Busca técnicas en HTMLs usando múltiples estrategias.
"""

import os
import re
import json
import sqlite3
import sys
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(text):
    print(f"\n{Colors.CYAN}➜ {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")

def find_html_files():
    print_step("🔍 Buscando archivos HTML...")
    search_paths = [
        '.',
        '/workspaces/Redaccion_castellana_curso',
        '/workspaces/Redaccion_castellana_curso/ejercicios_completos-lengua-castellana',
        '/home/codespace/backup_htmls',
    ]
    html_files = []
    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.html'):
                    fp = os.path.join(root, file)
                    if 'venv' not in fp and 'site-packages' not in fp and 'node_modules' not in fp:
                        html_files.append(fp)
    return html_files

def extract_techniques_from_html(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return []

    techniques = []
    seen = set()

    # Estrategia 1: Buscar en scripts
    script_pattern = r'<script[^>]*>([\s\S]*?)</script>'
    scripts = re.findall(script_pattern, content)
    for script in scripts:
        patterns = [
            r'\{[^{}]*"root"[^{}]*"meaning"[^{}]*\}',
            r'\{[^{}]*"raiz"[^{}]*"significado"[^{}]*\}',
            r'\{[^{}]*"técnica"[^{}]*"descripción"[^{}]*\}',
            r'\{[^{}]*"tecnica"[^{}]*"definicion"[^{}]*\}',
            r'\{[^{}]*"title"[^{}]*"description"[^{}]*\}',
            r'\{[^{}]*"name"[^{}]*"desc"[^{}]*\}',
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, script):
                try:
                    data_str = re.sub(r'(\w+):', r'"\1":', match.group())
                    data_str = re.sub(r"'", '"', data_str)
                    data = json.loads(data_str)
                    tec = data.get('root') or data.get('raiz') or data.get('técnica') or data.get('tecnica') or data.get('title') or data.get('name') or ''
                    defi = data.get('meaning') or data.get('significado') or data.get('descripción') or data.get('description') or data.get('desc') or data.get('definicion') or ''
                    if tec and defi and len(tec) > 2 and len(defi) > 2:
                        tec = re.sub(r'[^\w\sáéíóúñ\-\.\,\;]', '', tec).strip()
                        defi = re.sub(r'[^\w\sáéíóúñ\-\.\,\;]', '', defi).strip()
                        if tec and defi and tec not in seen:
                            seen.add(tec)
                            techniques.append({
                                'root': tec[:100],
                                'meaning': defi[:500],
                                'example': str(data.get('example', data.get('ejemplo', '')))[:500],
                                'breakdown': str(data.get('breakdown', data.get('desglose', '')))[:500]
                            })
                except:
                    pass

    # Estrategia 2: Divs
    div_pattern = r'<div[^>]*class="[^"]*(?:tecnica|técnica|card|item|lesson|flashcard)[^"]*"[^>]*>([\s\S]*?)</div>'
    for match in re.finditer(div_pattern, content, re.I):
        div_content = match.group(1)
        text = re.sub(r'<[^>]+>', ' ', div_content)
        text = re.sub(r'\s+', ' ', text).strip()
        if ':' in text and len(text) > 20:
            parts = text.split(':', 1)
            if len(parts) == 2:
                tec = parts[0].strip()
                defi = parts[1].strip()
                if len(tec) > 2 and len(defi) > 5 and tec not in seen:
                    seen.add(tec)
                    techniques.append({
                        'root': tec[:80],
                        'meaning': defi[:300],
                        'example': '',
                        'breakdown': ''
                    })

    # Estrategia 3: Listas
    li_pattern = r'<li[^>]*>([\s\S]*?)</li>'
    for match in re.finditer(li_pattern, content, re.I):
        li_content = match.group(1)
        text = re.sub(r'<[^>]+>', ' ', li_content)
        text = re.sub(r'\s+', ' ', text).strip()
        if ':' in text and len(text) > 15:
            parts = text.split(':', 1)
            if len(parts) == 2:
                tec = parts[0].strip()
                defi = parts[1].strip()
                if len(tec) > 2 and len(defi) > 3 and tec not in seen:
                    seen.add(tec)
                    techniques.append({
                        'root': tec[:80],
                        'meaning': defi[:300],
                        'example': '',
                        'breakdown': ''
                    })

    # Estrategia 4: Párrafos con números
    p_pattern = r'<p[^>]*>([\s\S]*?)</p>'
    for match in re.finditer(p_pattern, content, re.I):
        p_content = match.group(1)
        text = re.sub(r'<[^>]+>', ' ', p_content)
        text = re.sub(r'\s+', ' ', text).strip()
        m = re.search(r'(\d+)[\.\)]\s*([^:]+):\s*(.+?)(?=\.\s|$)', text)
        if m:
            tec = m.group(2).strip()
            defi = m.group(3).strip()
            if len(tec) > 3 and len(defi) > 5 and tec not in seen:
                seen.add(tec)
                techniques.append({
                    'root': tec[:80],
                    'meaning': defi[:300],
                    'example': '',
                    'breakdown': ''
                })

    return techniques

def detect_course_slug(file_path):
    file_name = os.path.basename(file_path).lower()
    course_map = {
        'etimologia': ['etimologia', 'raiz', 'grecolatinas', 'prefijo', 'sufijo'],
        'gramatica': ['gramatica', 'gramática', 'morfologia', 'morfosintaxis'],
        'retorica': ['retorica', 'retórica', 'figura', 'metafora', 'simil'],
        'ortografia': ['ortografia', 'ortografía', 'signos', 'coma', 'tilde'],
        'narracion': ['narracion', 'narración', 'cuento', 'historia', 'relato'],
        'exposicion': ['exposicion', 'exposición', 'ensayo', 'definir'],
        'argumentacion': ['argumentacion', 'argumentación', 'tesis', 'persuasion'],
        'descripcion': ['descripcion', 'descripción', 'adjetivo', 'calificativo'],
        'conectores': ['conector', 'cohesion', 'anfora', 'catafora'],
        'puntuacion': ['puntuacion', 'puntuación'],
        'perifrasis': ['perifrasis', 'perífrasis', 'verbal'],
        'fonetica': ['fonetica', 'fonética', 'sonido', 'vocal'],
        'comparacion': ['comparacion', 'comparación', 'comparativo'],
        'sintaxis': ['sintaxis', 'sintáctico', 'oracion'],
        'literatura': ['literatura', 'novela', 'poema', 'escritor'],
        'poesia': ['poesia', 'poesía', 'poema', 'verso'],
        'redaccion_avanzada': ['redaccion avanzada', 'redacción avanzada'],
        'comunicacion': ['comunicacion', 'comunicación', 'mensaje'],
        'academica': ['academica', 'académica', 'tesis'],
        'cientifica': ['cientifica', 'científica', 'experimento'],
        'periodistica': ['periodistica', 'periodística', 'noticia', 'reportaje'],
    }
    for slug, keywords in course_map.items():
        for kw in keywords:
            if kw in file_name:
                return slug
    return 'general'

def save_techniques_to_db(techniques, course_slug, conn):
    cursor = conn.cursor()
    # Obtener o crear curso
    cursor.execute("SELECT id FROM core_course WHERE slug = ?", (course_slug,))
    result = cursor.fetchone()
    if not result:
        # Insertar curso con order = 0
        cursor.execute("""
            INSERT INTO core_course (slug, name, description, icon, category, is_active, "order")
            VALUES (?, ?, ?, ?, ?, 1, 0)
        """, (course_slug, course_slug.replace('_', ' ').title(), f'100 técnicas de {course_slug}', '📚', course_slug))
        course_id = cursor.lastrowid
        print_success(f"Curso creado: {course_slug}")
    else:
        course_id = result[0]
    
    saved = 0
    for data in techniques:
        cursor.execute("SELECT id FROM core_lesson WHERE course_id = ? AND root = ?", (course_id, data['root']))
        if cursor.fetchone():
            continue
        cursor.execute("SELECT COUNT(*) FROM core_lesson WHERE course_id = ?", (course_id,))
        count = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO core_lesson 
            (course_id, "order", title, root, meaning, example, breakdown, is_active, difficulty, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'intermediate', 5)
        """, (course_id, count + 1, data['root'][:80], data['root'][:80], data['meaning'][:300], data['example'][:300] if data['example'] else '', data['breakdown'][:300] if data['breakdown'] else ''))
        saved += 1
    return saved

def main():
    print_header("📦 POBLADOR AUTOMÁTICO DEL ARCHIVO DE VECTOR")
    
    db_path = 'db.sqlite3'
    if not os.path.exists(db_path):
        print_error("Base de datos no encontrada. Ejecuta: python manage.py migrate")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    html_files = find_html_files()
    print(f"📄 Encontrados {len(html_files)} archivos HTML")
    
    total_techniques = 0
    files_processed = 0
    
    for idx, file_path in enumerate(html_files):
        if idx % 50 == 0:
            print(f"📂 Procesando archivo {idx+1}/{len(html_files)}")
        techniques = extract_techniques_from_html(file_path)
        if techniques:
            course_slug = detect_course_slug(file_path)
            saved = save_techniques_to_db(techniques[:20], course_slug, conn)
            if saved > 0:
                total_techniques += saved
                files_processed += 1
                print_success(f"  {os.path.basename(file_path)}: {saved} técnicas → {course_slug}")
    
    conn.commit()
    conn.close()
    
    print_header("📊 RESULTADOS")
    print(f"  📄 Archivos procesados: {files_processed}")
    print(f"  📚 Técnicas extraídas: {total_techniques}")
    print(f"\n  {Colors.CYAN}🌐 Accede a: http://localhost:8000{Colors.END}")
    print(f"  {Colors.CYAN}🔑 Admin: http://localhost:8000/admin{Colors.END}")

if __name__ == "__main__":
    main()
