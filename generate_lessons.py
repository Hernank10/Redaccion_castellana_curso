#!/usr/bin/env python
import os
import sqlite3
import random
import re

print("🤖 GENERADOR AUTOMÁTICO DE LECCIONES")
print("=" * 50)

# Conectar a la base de datos
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# TEMPLATES POR CATEGORÍA
templates = {
    'etimologia': {
        'prefixes': ['bio', 'geo', 'chrono', 'philo', 'sophia', 'demos', 'polis', 'theos', 'anthropos', 'logos', 'pathos', 'psyche', 'techne', 'phone', 'grapho', 'hydro', 'pneuma', 'soma', 'glossa', 'nomos'],
        'suffixes': ['-logía', '-grafía', '-metría', '-scopio', '-fono', '-patía', '-terapia', '-filia', '-fobia', '-manía'],
        'meanings': ['vida', 'tierra', 'tiempo', 'amor', 'sabiduría', 'pueblo', 'ciudad', 'dios', 'hombre', 'estudio', 'sentimiento', 'alma', 'arte', 'sonido', 'escribir', 'agua', 'aliento', 'cuerpo', 'lengua', 'ley']
    },
    'narracion': {
        'templates': [
            ('Érase una vez', 'Inicio de cuento tradicional', 'Estructura clásica de apertura'),
            ('Había una vez', 'Inicio de cuento infantil', 'Fórmula tradicional de inicio'),
            ('En un lugar de la Mancha', 'Inicio literario', 'Apertura de novela clásica'),
            ('De repente', 'Cambio brusco en la acción', 'Giro narrativo inesperado'),
            ('Mientras tanto', 'Simultaneidad de acciones', 'Acción paralela en la narración'),
            ('Al final', 'Conclusión de la narración', 'Cierre del relato'),
            ('Cuando llegó', 'Introducción temporal', 'Marca el momento de llegada'),
            ('Después de', 'Posterioridad temporal', 'Orden cronológico de eventos'),
            ('Antes de', 'Anterioridad temporal', 'Orden cronológico de eventos'),
            ('Durante', 'Transcurso de tiempo', 'Duración de la acción'),
            ('Apenas', 'Inmediatez temporal', 'Acción que acaba de ocurrir'),
            ('Tan pronto como', 'Inmediatez', 'Acción que ocurre inmediatamente'),
            ('Acto seguido', 'Continuación inmediata', 'Acción siguiente sin pausa'),
            ('De inmediato', 'Reacción rápida', 'Acción sin demora'),
            ('Sin demora', 'Urgencia en la acción', 'Acción sin pausa'),
            ('De golpe', 'Sorpresa inesperada', 'Cambio repentino en la narración'),
            ('Por fin', 'Resolución esperada', 'Final de la espera'),
            ('Al cabo de', 'Transcurso de tiempo', 'Paso del tiempo'),
            ('Días después', 'Salto temporal', 'Avance en el tiempo'),
            ('En aquel entonces', 'Tiempo pasado', 'Referencia al pasado'),
        ]
    },
    'gramatica': {
        'templates': [
            ('El sustantivo', 'Nombra personas, animales, cosas o ideas', 'Categoría gramatical'),
            ('El adjetivo', 'Acompaña al sustantivo y expresa cualidades', 'Categoría gramatical'),
            ('El verbo', 'Expresa acción, estado o proceso', 'Categoría gramatical'),
            ('El adverbio', 'Modifica al verbo, adjetivo u otro adverbio', 'Categoría gramatical'),
            ('La preposición', 'Relaciona elementos de la oración', 'Categoría gramatical'),
            ('La conjunción', 'Une oraciones o elementos', 'Categoría gramatical'),
            ('El artículo', 'Acompaña al sustantivo', 'Categoría gramatical'),
            ('El pronombre', 'Sustituye al sustantivo', 'Categoría gramatical'),
            ('Concordancia nominal', 'Relación de género y número', 'Concordancia gramatical'),
            ('Concordancia verbal', 'Relación de número y persona', 'Concordancia gramatical'),
            ('Oración simple', 'Un solo verbo conjugado', 'Estructura sintáctica'),
            ('Oración compuesta', 'Más de un verbo conjugado', 'Estructura sintáctica'),
            ('Sujeto', 'Quién realiza la acción', 'Elemento de la oración'),
            ('Predicado', 'Lo que se dice del sujeto', 'Elemento de la oración'),
            ('Complemento directo', 'Recibe la acción del verbo', 'Complemento verbal'),
            ('Complemento indirecto', 'Destinatario de la acción', 'Complemento verbal'),
            ('Complemento circunstancial', 'Expresa circunstancias', 'Complemento verbal'),
            ('Oración subordinada', 'Depende de otra oración', 'Tipo de oración'),
            ('Verbos regulares', 'Siguen un patrón de conjugación', 'Conjugación verbal'),
            ('Verbos irregulares', 'No siguen un patrón', 'Conjugación verbal'),
        ]
    },
    'retorica': {
        'templates': [
            ('Metáfora', 'Comparación implícita entre dos términos', 'Figura retórica'),
            ('Símil', 'Comparación explícita con "como"', 'Figura retórica'),
            ('Hipérbole', 'Exageración intencionada', 'Figura retórica'),
            ('Ironía', 'Decir lo contrario de lo que se piensa', 'Figura retórica'),
            ('Antítesis', 'Contraposición de ideas contrarias', 'Figura retórica'),
            ('Paradoja', 'Contradicción aparente', 'Figura retórica'),
            ('Personificación', 'Atribuir cualidades humanas', 'Figura retórica'),
            ('Aliteración', 'Repetición de sonidos', 'Figura retórica'),
            ('Anáfora', 'Repetición al inicio de versos', 'Figura retórica'),
            ('Epífora', 'Repetición al final de versos', 'Figura retórica'),
            ('Asíndeton', 'Omisión de conjunciones', 'Figura retórica'),
            ('Polisíndeton', 'Uso excesivo de conjunciones', 'Figura retórica'),
            ('Hipérbaton', 'Alteración del orden lógico', 'Figura retórica'),
            ('Oxímoron', 'Unión de términos contradictorios', 'Figura retórica'),
            ('Sinécdoque', 'Parte por el todo o viceversa', 'Figura retórica'),
            ('Metonimia', 'Sustitución por relación de contigüidad', 'Figura retórica'),
            ('Eufemismo', 'Sustitución de término desagradable', 'Figura retórica'),
            ('Prosopopeya', 'Personificación de objetos abstractos', 'Figura retórica'),
            ('Apóstrofe', 'Interpelación a alguien o algo', 'Figura retórica'),
            ('Gradación', 'Orden ascendente o descendente', 'Figura retórica'),
        ]
    },
    'ortografia': {
        'templates': [
            ('Uso de la b', 'Se escribe b antes de consonante', 'Regla ortográfica'),
            ('Uso de la v', 'Se escribe v después de n', 'Regla ortográfica'),
            ('Uso de la g', 'Se escribe g ante e, i', 'Regla ortográfica'),
            ('Uso de la j', 'Se escribe j en verbos terminados en -jer', 'Regla ortográfica'),
            ('Uso de la h', 'Se escribe h en palabras que comienzan con hue-', 'Regla ortográfica'),
            ('Palabras agudas', 'Llevan tilde al final en vocal, n o s', 'Regla de acentuación'),
            ('Palabras graves', 'Llevan tilde si NO terminan en vocal, n o s', 'Regla de acentuación'),
            ('Palabras esdrújulas', 'Siempre llevan tilde', 'Regla de acentuación'),
            ('Palabras sobresdrújulas', 'Siempre llevan tilde', 'Regla de acentuación'),
            ('Tilde diacrítica', 'Distingue palabras de igual forma', 'Regla de acentuación'),
            ('Uso de la c', 'Se escribe c ante e, i', 'Regla ortográfica'),
            ('Uso de la z', 'Se escribe z ante a, o, u', 'Regla ortográfica'),
            ('Uso de la ll', 'Se escribe ll en palabras que comienzan con cha-', 'Regla ortográfica'),
            ('Uso de la y', 'Se escribe y en palabras que terminan en -y', 'Regla ortográfica'),
            ('Uso de la r', 'Se escribe r al inicio de palabra', 'Regla ortográfica'),
            ('Uso de la rr', 'Se escribe rr entre vocales', 'Regla ortográfica'),
            ('Uso de la x', 'Se escribe x en palabras que comienzan con ex-', 'Regla ortográfica'),
            ('Mayúsculas', 'Se usan al inicio de oración y nombres propios', 'Regla ortográfica'),
            ('Minúsculas', 'Se usan en el resto de casos', 'Regla ortográfica'),
            ('Acentuación de interrogativos', 'Llevan tilde en preguntas', 'Regla de acentuación'),
        ]
    }
}

# Generar lecciones para cada curso
def generate_lessons_for_course(course_slug, course_name, target_count=20):
    """Genera lecciones para un curso específico"""
    cursor.execute("SELECT id FROM core_course WHERE slug = ?", (course_slug,))
    course = cursor.fetchone()
    
    if not course:
        print(f'❌ Curso no encontrado: {course_slug}')
        return 0
    
    course_id = course[0]
    
    # Verificar cuántas lecciones tiene actualmente
    cursor.execute("SELECT COUNT(*) FROM core_lesson WHERE course_id = ?", (course_id,))
    current_count = cursor.fetchone()[0]
    
    if current_count >= target_count:
        print(f'ℹ️ {course_name}: ya tiene {current_count} lecciones (objetivo: {target_count})')
        return 0
    
    # Obtener template para la categoría
    template = templates.get(course_slug)
    if not template:
        print(f'⚠️ No hay template para: {course_slug}')
        return 0
    
    # Generar lecciones
    generated = 0
    for i in range(current_count + 1, target_count + 1):
        # Seleccionar un template aleatorio (o usar índice)
        template_data = template['templates'][i % len(template['templates'])]
        
        if isinstance(template_data, tuple):
            root, meaning, breakdown = template_data
            example = f'Ejemplo de uso: "{root}"'
        else:
            # Para etimología
            if 'prefixes' in template:
                prefix = random.choice(template['prefixes'])
                suffix = random.choice(template['suffixes'])
                meaning = random.choice(template['meanings'])
                root = f"{prefix}{suffix}"
                example = f"Palabra derivada: {root}"
                breakdown = f"Raíz {prefix} + sufijo {suffix}"
            else:
                continue
        
        cursor.execute("""
            INSERT INTO core_lesson 
            (course_id, "order", title, root, meaning, example, breakdown, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (course_id, i, root[:80], root[:80], meaning[:300], example[:300] if example else '', breakdown[:300] if breakdown else ''))
        generated += 1
    
    conn.commit()
    print(f'✅ {course_name}: +{generated} lecciones (total: {current_count + generated})')
    return generated

# Cursos a generar
courses_to_generate = {
    'etimologia': 'Raíces y Etimología',
    'narracion': 'Fórmulas de Narración',
    'gramatica': 'Gramática del Castellano',
    'retorica': 'Figuras Retóricas',
    'ortografia': 'Ortografía Castellana',
}

total_generated = 0
for slug, name in courses_to_generate.items():
    total_generated += generate_lessons_for_course(slug, name, 20)

print(f'\n{"=" * 50}')
print(f'🎉 TOTAL GENERADO: {total_generated} lecciones')

conn.close()
