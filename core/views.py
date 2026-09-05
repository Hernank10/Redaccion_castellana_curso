from django.db import models
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
import uuid

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.urls import reverse
from .models import Course, Lesson, Exercise, UserProgress, UserScore, UserStreak
import json

# ===== VISTAS PÚBLICAS =====
def index(request):
    courses = Course.objects.filter(is_active=True)
    total_lessons = sum(c.lessons.count() for c in courses)
    return render(request, 'core/index.html', {
        'courses': courses,
        'total_lessons': total_lessons,
        'total_courses': courses.count(),
    })

def course_detail(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    lessons = course.lessons.filter(is_active=True)
    progress = {}
    if request.user.is_authenticated:
        for lesson in lessons:
            prog = UserProgress.objects.filter(user=request.user, lesson=lesson).first()
            progress[lesson.id] = {
                'completed': prog.completed if prog else False,
                'score': prog.score if prog else 0,
            }
    return render(request, 'core/lesson_detail.html', {
        'course': course,
        'lessons': lessons,
        'progress': progress,
    })

def get_lesson_data(request, course_slug, lesson_order):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, order=lesson_order)
    exercises = lesson.exercises.all()
    data = {
        'id': lesson.id,
        'title': lesson.title,
        'root': lesson.root,
        'meaning': lesson.meaning,
        'example': lesson.example,
        'breakdown': lesson.breakdown,
        'exercises': [
            {
                'id': ex.id,
                'question': ex.question,
                'options': [ex.option_a, ex.option_b, ex.option_c, ex.option_d],
                'correct': ex.correct_answer,
            } for ex in exercises
        ],
        'total_lessons': course.lessons.count(),
    }
    return JsonResponse(data)

@login_required
def save_lesson_progress(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lesson_id = data.get('lesson_id')
            score = data.get('score', 0)
            completed = data.get('completed', False)
            lesson = get_object_or_404(Lesson, id=lesson_id)
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson
            )
            progress.attempts += 1
            if score > progress.score:
                progress.score = score
            if completed:
                progress.completed = True
            progress.save()
            user_score, _ = UserScore.objects.get_or_create(user=request.user)
            user_score.total_points += score
            user_score.lessons_completed = UserProgress.objects.filter(
                user=request.user, completed=True
            ).count()
            user_score.save()
            streak, _ = UserStreak.objects.get_or_create(user=request.user)
            if completed:
                streak.current_streak += 1
                if streak.current_streak > streak.max_streak:
                    streak.max_streak = streak.current_streak
            streak.save()
            return JsonResponse({
                'status': 'success',
                'points': score,
                'completed': progress.completed,
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def dashboard(request):
    user_score = UserScore.objects.get_or_create(user=request.user)[0]
    streak = UserStreak.objects.get_or_create(user=request.user)[0]
    progress_count = UserProgress.objects.filter(user=request.user, completed=True).count()
    course_progress = {}
    total_lessons = 0
    completed_lessons = 0
    for course in Course.objects.filter(is_active=True):
        total = course.lessons.count()
        completed = UserProgress.objects.filter(
            user=request.user, lesson__course=course, completed=True
        ).count()
        course_progress[course.id] = {
            'name': course.name,
            'icon': course.icon,
            'total': total,
            'completed': completed,
            'percentage': round((completed / total * 100) if total > 0 else 0),
        }
        total_lessons += total
        completed_lessons += completed
    return render(request, 'core/dashboard.html', {
        'user_score': user_score,
        'streak': streak,
        'progress_count': progress_count,
        'course_progress': course_progress,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
    })

def practice_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, is_active=True)
    exercises = lesson.exercises.all()
    exercises_data = []
    for ex in exercises:
        exercises_data.append({
            'id': ex.id,
            'question': ex.question,
            'options': [ex.option_a, ex.option_b, ex.option_c, ex.option_d],
            'correct': ex.correct_answer,
            'explanation': ex.explanation,
        })
    return render(request, 'core/practice.html', {
        'lesson': lesson,
        'exercises': exercises_data,
    })

# ===== VISTAS PARA PROFESORES =====
@staff_member_required
def teacher_dashboard(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'core/teacher_dashboard.html', {'courses': courses})

@staff_member_required
def teacher_lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    exercises = lesson.exercises.all()
    return render(request, 'core/teacher_lesson_detail.html', {
        'lesson': lesson,
        'exercises': exercises,
    })

@staff_member_required
def teacher_exercise_edit(request, exercise_id=None):
    lesson = None
    exercise = None
    if exercise_id:
        exercise = get_object_or_404(Exercise, id=exercise_id)
        lesson = exercise.lesson
    else:
        lesson_id = request.GET.get('lesson_id')
        if not lesson_id:
            return redirect('teacher_dashboard')
        lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        exercise_type = request.POST.get('exercise_type')
        question = request.POST.get('question')
        option_a = request.POST.get('option_a', '')
        option_b = request.POST.get('option_b', '')
        option_c = request.POST.get('option_c', '')
        option_d = request.POST.get('option_d', '')
        correct_answer = request.POST.get('correct_answer')
        explanation = request.POST.get('explanation', '')
        points = request.POST.get('points', 1)
        is_active = request.POST.get('is_active') == 'on'

        if exercise:
            exercise.exercise_type = exercise_type
            exercise.question = question
            exercise.option_a = option_a
            exercise.option_b = option_b
            exercise.option_c = option_c
            exercise.option_d = option_d
            exercise.correct_answer = correct_answer
            exercise.explanation = explanation
            exercise.points = points
            exercise.is_active = is_active
            exercise.save()
        else:
            Exercise.objects.create(
                lesson=lesson,
                exercise_type=exercise_type,
                question=question,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer,
                explanation=explanation,
                points=points,
                is_active=is_active,
            )
        return redirect('teacher_lesson_detail', lesson_id=lesson.id)

    return render(request, 'core/teacher_exercise_edit.html', {
        'exercise': exercise,
        'lesson': lesson,
    })

@staff_member_required
def teacher_exercise_delete(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id)
    lesson_id = exercise.lesson.id
    exercise.delete()
    return redirect('teacher_lesson_detail', lesson_id=lesson_id)

from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import qrcode
import uuid
import os
from django.conf import settings

@login_required
def generar_certificado(request, leccion_id=None, curso_slug=None):
    """Genera un certificado en PDF para el usuario"""
    user = request.user
    
    # Obtener progreso del usuario
    if leccion_id:
        leccion = get_object_or_404(Lesson, id=leccion_id, is_active=True)
        curso = leccion.course
        ejercicios = leccion.exercises.filter(is_active=True)
        total_ejercicios = ejercicios.count()
        completados = UserProgress.objects.filter(
            user=user, lesson=leccion, completed=True
        ).count()
        puntuacion = UserProgress.objects.filter(
            user=user, lesson=leccion
        ).aggregate(total=models.Sum('score'))['total'] or 0
        titulo = f"Lección: {leccion.title}"
        slug = f"leccion-{leccion.id}"
    elif curso_slug:
        curso = get_object_or_404(Course, slug=curso_slug, is_active=True)
        lecciones = curso.lessons.filter(is_active=True)
        total_ejercicios = sum(l.exercises.count() for l in lecciones)
        completados = UserProgress.objects.filter(
            user=user, lesson__course=curso, completed=True
        ).count()
        puntuacion = UserProgress.objects.filter(
            user=user, lesson__course=curso
        ).aggregate(total=models.Sum('score'))['total'] or 0
        titulo = f"Curso: {curso.name}"
        slug = curso_slug
        leccion = None
    else:
        return HttpResponse("No se especificó lección o curso", status=400)
    
    # Calcular porcentaje
    porcentaje = int((completados / total_ejercicios * 100)) if total_ejercicios > 0 else 0
    
    # Verificar si ya existe un certificado
    certificado, creado = Certificado.objects.get_or_create(
        usuario=user,
        curso=curso,
        leccion=leccion,
        defaults={
            'titulo': titulo,
            'puntuacion': puntuacion,
            'ejercicios_completados': completados,
            'total_ejercicios': total_ejercicios,
            'porcentaje': porcentaje,
            'codigo_verificacion': f"VECTOR-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:4].upper()}"
        }
    )
    
    if not creado:
        # Actualizar datos existentes
        certificado.puntuacion = puntuacion
        certificado.ejercicios_completados = completados
        certificado.total_ejercicios = total_ejercicios
        certificado.porcentaje = porcentaje
        certificado.save()
    
    # Generar PDF
    pdf = generar_pdf_certificado(
        user=user,
        titulo=titulo,
        curso=curso,
        completados=completados,
        total_ejercicios=total_ejercicios,
        porcentaje=porcentaje,
        puntuacion=puntuacion,
        codigo=certificado.codigo_verificacion,
        fecha=certificado.fecha_emision
    )
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="certificado_{slug}_{user.username}.pdf"'
    return response

def generar_pdf_certificado(user, titulo, curso, completados, total_ejercicios, porcentaje, puntuacion, codigo, fecha):
    """Genera el PDF del certificado"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        topMargin=1*cm,
        bottomMargin=1*cm,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    style_titulo = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=36,
        textColor=colors.HexColor('#00f0ff'),
        alignment=TA_CENTER,
        spaceAfter=0.5*cm
    )
    
    style_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#b000ff'),
        alignment=TA_CENTER,
        spaceAfter=1*cm
    )
    
    style_nombre = ParagraphStyle(
        'Nombre',
        parent=styles['Heading1'],
        fontSize=42,
        textColor=colors.HexColor('#ffffff'),
        alignment=TA_CENTER,
        spaceAfter=0.8*cm,
        fontName='Helvetica-Bold'
    )
    
    style_texto = ParagraphStyle(
        'Texto',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#e0e0ff'),
        alignment=TA_CENTER,
        spaceAfter=0.3*cm
    )
    
    style_codigo = ParagraphStyle(
        'Codigo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666688'),
        alignment=TA_CENTER
    )
    
    # Generar elementos del PDF
    story = []
    
    # Título
    story.append(Paragraph("📜 CERTIFICADO DE FINALIZACIÓN", style_titulo))
    story.append(Spacer(1, 0.3*cm))
    
    # Subtítulo
    story.append(Paragraph(f"<b>{titulo}</b>", style_subtitulo))
    story.append(Spacer(1, 0.5*cm))
    
    # Nombre del usuario
    story.append(Paragraph(f"<b>{user.get_full_name() or user.username}</b>", style_nombre))
    story.append(Spacer(1, 0.5*cm))
    
    # Texto de certificación
    texto_cert = f"""
    Ha completado satisfactoriamente el programa de aprendizaje<br/>
    con un <b>{porcentaje}%</b> de ejercicios correctamente resueltos<br/>
    (<b>{completados}</b> de <b>{total_ejercicios}</b> ejercicios completados)<br/>
    obteniendo una puntuación de <b>{puntuacion}</b> puntos.
    """
    story.append(Paragraph(texto_cert, style_texto))
    story.append(Spacer(1, 0.5*cm))
    
    # Información del curso
    if curso:
        story.append(Paragraph(f"Curso: <b>{curso.name}</b>", style_texto))
        story.append(Spacer(1, 0.3*cm))
    
    # Fecha
    story.append(Paragraph(f"Fecha de emisión: {fecha.strftime('%d de %B de %Y')}", style_texto))
    story.append(Spacer(1, 0.5*cm))
    
    # Código de verificación
    story.append(Paragraph(f"Código de verificación: {codigo}", style_codigo))
    story.append(Spacer(1, 0.3*cm))
    
    # Pie de página
    story.append(Paragraph("El Archivo de Vector · Cronista Temporal", style_codigo))
    
    # Construir PDF
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# ===== CERTIFICADOS =====
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
import uuid
from django.db import models

@login_required
def generar_certificado(request, leccion_id=None, curso_slug=None):
    """Genera un certificado en PDF para el usuario"""
    user = request.user
    
    if leccion_id:
        leccion = get_object_or_404(Lesson, id=leccion_id, is_active=True)
        curso = leccion.course
        ejercicios = leccion.exercises.filter(is_active=True)
        total_ejercicios = ejercicios.count()
        completados = UserProgress.objects.filter(
            user=user, lesson=leccion, completed=True
        ).count()
        puntuacion = UserProgress.objects.filter(
            user=user, lesson=leccion
        ).aggregate(total=models.Sum('score'))['total'] or 0
        titulo = f"Lección: {leccion.title}"
        slug = f"leccion-{leccion.id}"
    elif curso_slug:
        curso = get_object_or_404(Course, slug=curso_slug, is_active=True)
        lecciones = curso.lessons.filter(is_active=True)
        total_ejercicios = sum(l.exercises.count() for l in lecciones)
        completados = UserProgress.objects.filter(
            user=user, lesson__course=curso, completed=True
        ).count()
        puntuacion = UserProgress.objects.filter(
            user=user, lesson__course=curso
        ).aggregate(total=models.Sum('score'))['total'] or 0
        titulo = f"Curso: {curso.name}"
        slug = curso_slug
        leccion = None
    else:
        return HttpResponse("No se especificó lección o curso", status=400)
    
    porcentaje = int((completados / total_ejercicios * 100)) if total_ejercicios > 0 else 0
    
    # Verificar si ya existe un certificado
    from core.models import Certificado
    certificado, creado = Certificado.objects.get_or_create(
        usuario=user,
        curso=curso,
        leccion=leccion,
        defaults={
            'titulo': titulo,
            'puntuacion': puntuacion,
            'ejercicios_completados': completados,
            'total_ejercicios': total_ejercicios,
            'porcentaje': porcentaje,
            'codigo_verificacion': f"VECTOR-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:4].upper()}"
        }
    )
    
    if not creado:
        certificado.puntuacion = puntuacion
        certificado.ejercicios_completados = completados
        certificado.total_ejercicios = total_ejercicios
        certificado.porcentaje = porcentaje
        certificado.save()
    
    # Generar PDF
    pdf = generar_pdf_certificado(
        user=user,
        titulo=titulo,
        curso=curso,
        completados=completados,
        total_ejercicios=total_ejercicios,
        porcentaje=porcentaje,
        puntuacion=puntuacion,
        codigo=certificado.codigo_verificacion,
        fecha=certificado.fecha_emision
    )
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="certificado_{slug}_{user.username}.pdf"'
    return response

def generar_pdf_certificado(user, titulo, curso, completados, total_ejercicios, porcentaje, puntuacion, codigo, fecha):
    """Genera el PDF del certificado"""
    from io import BytesIO
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        topMargin=1*cm,
        bottomMargin=1*cm,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    
    style_titulo = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=36,
        textColor=colors.HexColor('#00f0ff'),
        alignment=TA_CENTER,
        spaceAfter=0.5*cm
    )
    
    style_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#b000ff'),
        alignment=TA_CENTER,
        spaceAfter=1*cm
    )
    
    style_nombre = ParagraphStyle(
        'Nombre',
        parent=styles['Heading1'],
        fontSize=42,
        textColor=colors.HexColor('#ffffff'),
        alignment=TA_CENTER,
        spaceAfter=0.8*cm,
        fontName='Helvetica-Bold'
    )
    
    style_texto = ParagraphStyle(
        'Texto',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#e0e0ff'),
        alignment=TA_CENTER,
        spaceAfter=0.3*cm
    )
    
    style_codigo = ParagraphStyle(
        'Codigo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666688'),
        alignment=TA_CENTER
    )
    
    story = []
    story.append(Paragraph("📜 CERTIFICADO DE FINALIZACIÓN", style_titulo))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"<b>{titulo}</b>", style_subtitulo))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"<b>{user.get_full_name() or user.username}</b>", style_nombre))
    story.append(Spacer(1, 0.5*cm))
    
    texto_cert = f"""
    Ha completado satisfactoriamente el programa de aprendizaje<br/>
    con un <b>{porcentaje}%</b> de ejercicios correctamente resueltos<br/>
    (<b>{completados}</b> de <b>{total_ejercicios}</b> ejercicios completados)<br/>
    obteniendo una puntuación de <b>{puntuacion}</b> puntos.
    """
    story.append(Paragraph(texto_cert, style_texto))
    story.append(Spacer(1, 0.5*cm))
    
    if curso:
        story.append(Paragraph(f"Curso: <b>{curso.name}</b>", style_texto))
        story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph(f"Fecha de emisión: {fecha.strftime('%d de %B de %Y')}", style_texto))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Código de verificación: {codigo}", style_codigo))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("El Archivo de Vector · Cronista Temporal", style_codigo))
    
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
