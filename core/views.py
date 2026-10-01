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
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from core.notificaciones import crear_notificacion_curso_completado, crear_notificacion_evaluacion, crear_notificacion_certificado
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.urls import reverse
from .models import Course, Lesson, Exercise, UserProgress, UserScore, UserStreak, Inscripcion, Logro, Certificado, Evaluacion
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
    # Crear inscripción si no existe
    inscrito = False
    if request.user.is_authenticated:
        inscripcion, created = Inscripcion.objects.get_or_create(
            user=request.user, course=course
        )
        inscrito = True
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

            # Notificar si el curso se acaba de completar al 100%
            if completed:
                total_lecciones = lesson.course.lessons.count()
                completadas = UserProgress.objects.filter(
                    user=request.user, lesson__course=lesson.course, completed=True
                ).count()
                if total_lecciones > 0 and completadas >= total_lecciones:
                    from core.models import Notificacion
                    ya_notificado = Notificacion.objects.filter(
                        user=request.user, tipo='curso_completado', titulo__contains=lesson.course.name
                    ).exists()
                    if not ya_notificado:
                        crear_notificacion_curso_completado(request.user, lesson.course)

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
    user_score, _ = UserScore.objects.get_or_create(user=request.user)
    streak, _ = UserStreak.objects.get_or_create(user=request.user)
    progress_count = UserProgress.objects.filter(user=request.user, completed=True).count()

    # Solo cursos en los que está inscrito
    inscripciones = Inscripcion.objects.filter(user=request.user).select_related('course')
    course_progress = []
    total_lessons = 0
    completed_lessons = 0

    for insc in inscripciones:
        course = insc.course
        total = course.lessons.count()
        completed = UserProgress.objects.filter(
            user=request.user, lesson__course=course, completed=True
        ).count()
        porcentaje = round((completed / total * 100) if total > 0 else 0)
        course_progress.append({
            'course': course,
            'total': total,
            'completed': completed,
            'percentage': porcentaje,
        })
        total_lessons += total
        completed_lessons += completed

    logros = Logro.objects.filter(user=request.user)
    certificados = Certificado.objects.filter(usuario=request.user)

    return render(request, 'core/dashboard.html', {
        'user_score': user_score,
        'streak': streak,
        'progress_count': progress_count,
        'course_progress': course_progress,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'logros': logros,
        'certificados': certificados,
        'inscripciones_count': inscripciones.count(),
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
    from core.certificados import generar_pdf_certificado as _pdf_cert_nuevo
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


def course_list(request):
    from .models import Course, Inscripcion, Logro
    cursos = Course.objects.filter(is_active=True).order_by('order')
    return render(request, 'core/course_list.html', {'cursos': cursos})


def resource_list(request):
    from .models import Lesson, Inscripcion, Logro
    recursos = Lesson.objects.filter(is_active=True).select_related('course').order_by('course__order', 'order')
    return render(request, 'core/resource_list.html', {'recursos': recursos})


def registro(request):
    from django.contrib import messages
    from django.contrib.auth.models import User
    from django.shortcuts import redirect
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.error(request, 'Usuario y contrasena son obligatorios')
            return render(request, 'core/registro.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
            return render(request, 'core/registro.html')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Cuenta creada. Ahora puedes iniciar sesion.')
        return redirect('login')
    return render(request, 'core/registro.html')


@login_required
def perfil(request):
    """Pagina de perfil del estudiante."""
    user = request.user
    user_score, _ = UserScore.objects.get_or_create(user=user)
    streak, _ = UserStreak.objects.get_or_create(user=user)
    inscripciones = Inscripcion.objects.filter(user=user).count()
    certificados = Certificado.objects.filter(usuario=user).count()
    logros = Logro.objects.filter(user=user).count()
    progreso = UserProgress.objects.filter(user=user, completed=True).count()
    ultimos_logros = Logro.objects.filter(user=user).order_by("-fecha")[:5]
    ultimos_certs = Certificado.objects.filter(usuario=user).order_by("-fecha_emision")[:3]

    return render(request, 'core/perfil.html', {
        'user_score': user_score,
        'streak': streak,
        'inscripciones_count': inscripciones,
        'certificados_count': certificados,
        'logros_count': logros,
        'progreso_count': progreso,
        'ultimos_logros': ultimos_logros,
        'ultimos_certs': ultimos_certs,
    })


# ============================================================
# CERTIFICADO PDF MEJORADO (estilo diploma)
# ============================================================
def generar_pdf_certificado_v2(user, titulo, curso, completados, total_ejercicios,
                                 porcentaje, puntuacion, codigo, fecha):
    """Genera un certificado PDF con diseño tipo diploma."""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor, black, white
    from io import BytesIO
    import qrcode

    buffer = BytesIO()
    W, H = landscape(A4)  # 842 x 595
    c = canvas.Canvas(buffer, pagesize=(W, H))

    # Colores
    dorado = HexColor("#C9A227")
    azul_oscuro = HexColor("#0a0e27")
    azul_claro = HexColor("#00d4ff")
    gris = HexColor("#4a4a4a")

    # === FONDO ===
    c.setFillColor(azul_oscuro)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Marco exterior dorado
    c.setStrokeColor(dorado)
    c.setLineWidth(6)
    c.rect(20, 20, W-40, H-40, fill=0, stroke=1)

    # Marco interior fino
    c.setStrokeColor(dorado)
    c.setLineWidth(1.5)
    c.rect(30, 30, W-60, H-60, fill=0, stroke=1)

    # Esquinas decorativas
    c.setStrokeColor(dorado)
    c.setLineWidth(3)
    esquina = 40
    # Superior izquierda
    c.line(35, H-35-esquina, 35, H-35); c.line(35, H-35, 35+esquina, H-35)
    # Superior derecha
    c.line(W-35, H-35-esquina, W-35, H-35); c.line(W-35, H-35, W-35-esquina, H-35)
    # Inferior izquierda
    c.line(35, 35+esquina, 35, 35); c.line(35, 35, 35+esquina, 35)
    # Inferior derecha
    c.line(W-35, 35+esquina, W-35, 35); c.line(W-35, 35, W-35-esquina, 35)

    # === ENCABEZADO ===
    c.setFillColor(azul_claro)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, H-70, "⌛ ARCHIVO DE VECTOR")

    c.setFillColor(dorado)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W/2, H-88, "CRONISTA TEMPORAL · 1000 TÉCNICAS DE REDACCIÓN")

    # Línea decorativa
    c.setStrokeColor(dorado)
    c.setLineWidth(1)
    c.line(W/2-150, H-100, W/2+150, H-100)

    # === TÍTULO ===
    c.setFillColor(dorado)
    c.setFont("Times-Bold", 38)
    c.drawCentredString(W/2, H-150, "CERTIFICADO")

    c.setFillColor(white)
    c.setFont("Times-Italic", 14)
    c.drawCentredString(W/2, H-172, "de finalización")

    # === CUERPO ===
    c.setFillColor(white)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W/2, H-210, "Se otorga el presente certificado a")

    # Nombre del estudiante
    nombre = user.get_full_name() or user.username
    c.setFillColor(azul_claro)
    c.setFont("Times-BoldItalic", 32)
    c.drawCentredString(W/2, H-255, nombre.upper())

    # Línea bajo el nombre
    ancho_nombre = c.stringWidth(nombre.upper(), "Times-BoldItalic", 32)
    c.setStrokeColor(dorado)
    c.setLineWidth(1)
    c.line(W/2-ancho_nombre/2-20, H-262, W/2+ancho_nombre/2+20, H-262)

    # Texto
    c.setFillColor(white)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W/2, H-290, "por haber completado satisfactoriamente el curso")

    # Curso
    c.setFillColor(dorado)
    c.setFont("Times-Bold", 20)
    curso_nombre = curso.name if hasattr(curso, 'name') else str(curso)
    c.drawCentredString(W/2, H-320, curso_nombre)

    # Estadísticas
    c.setFillColor(white)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H-345,
        f"{completados} de {total_ejercicios} lecciones completadas · "
        f"{porcentaje}% · {puntuacion} puntos")

    # === FECHA Y FIRMA (abajo izquierda) ===
    c.setFillColor(white)
    c.setFont("Helvetica", 10)
    fecha_str = fecha.strftime("%d de %B de %Y") if hasattr(fecha, 'strftime') else str(fecha)
    c.drawString(80, 110, f"Fecha de emisión:")
    c.setFillColor(dorado)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(80, 95, fecha_str)

    # Firma (abajo centro-derecha)
    c.setStrokeColor(white)
    c.setLineWidth(1)
    c.line(W-250, 105, W-80, 105)
    c.setFillColor(white)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W-165, 90, "Dirección Académica")

    # === CÓDIGO DE VERIFICACIÓN (arriba derecha) ===
    c.setFillColor(dorado)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(W-260, H-130, "CÓDIGO DE VERIFICACIÓN:")
    c.setFillColor(white)
    c.setFont("Courier", 9)
    c.drawString(W-260, H-142, codigo)

    # === QR (abajo derecha) ===
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(f"https://archivodevector.com/verificar/{codigo}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        from reportlab.lib.utils import ImageReader
        c.drawImage(ImageReader(qr_buffer), W-130, 55, width=70, height=70)
        c.setFillColor(gris)
        c.setFont("Helvetica", 7)
        c.drawCentredString(W-95, 48, "Escanear para verificar")
    except Exception as e:
        pass

    # Pie de página
    c.setFillColor(gris)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W/2, 45, "Este certificado puede verificarse en archivodevector.com con el código indicado")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ============================================================
# CERTIFICADO WORD
# ============================================================
def generar_docx_certificado(user, titulo, curso, completados, total_ejercicios,
                              porcentaje, puntuacion, codigo, fecha):
    """Genera un certificado Word (.docx) con diseño."""
    from io import BytesIO

    try:
        from docx import Document
        from docx.shared import Pt, Cm, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.section import WD_ORIENT
    except ImportError:
        raise ImportError("Instala python-docx: pip install python-docx")

    doc = Document()

    # Configurar página horizontal
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = section.page_height, section.page_width

    # Márgenes
    for m in ["top_margin", "bottom_margin", "left_margin", "right_margin"]:
        setattr(section, m, Cm(2))

    def add_centered(text, size, bold=False, italic=False, color=None, font="Calibri"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.name = font
        if color:
            run.font.color.rgb = RGBColor(*color)
        return p

    # Encabezado
    add_centered("⌛ ARCHIVO DE VECTOR", 14, bold=True, color=(0, 212, 255))
    add_centered("CRONISTA TEMPORAL · 1000 TÉCNICAS DE REDACCIÓN", 10, color=(120, 120, 120))

    doc.add_paragraph()

    # Título
    add_centered("CERTIFICADO", 40, bold=True, color=(201, 162, 39), font="Times New Roman")
    add_centered("de finalización", 14, italic=True, font="Times New Roman")

    doc.add_paragraph()
    add_centered("Se otorga el presente certificado a", 12)

    # Nombre
    nombre = user.get_full_name() or user.username
    add_centered(nombre.upper(), 32, bold=True, italic=True,
                 color=(0, 150, 200), font="Times New Roman")

    doc.add_paragraph()
    add_centered("por haber completado satisfactoriamente el curso", 12)

    curso_nombre = curso.name if hasattr(curso, 'name') else str(curso)
    add_centered(curso_nombre, 20, bold=True, color=(201, 162, 39),
                 font="Times New Roman")

    doc.add_paragraph()
    add_centered(f"{completados} de {total_ejercicios} lecciones completadas · {porcentaje}% · {puntuacion} puntos", 11)

    doc.add_paragraph()
    doc.add_paragraph()

    # Pie con tabla de 3 columnas
    table = doc.add_table(rows=1, cols=3)
    table.autofit = True

    # Columna 1: fecha
    cell = table.cell(0, 0)
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Fecha de emisión\n")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(120, 120, 120)
    fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, 'strftime') else str(fecha)
    run2 = p.add_run(fecha_str)
    run2.font.size = Pt(11)
    run2.font.bold = True
    run2.font.color.rgb = RGBColor(201, 162, 39)

    # Columna 2: firma
    cell = table.cell(0, 1)
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("_______________________\n")
    run2 = p.add_run("Dirección Académica")
    run2.font.size = Pt(10)

    # Columna 3: código
    cell = table.cell(0, 2)
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Código de verificación\n")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(120, 120, 120)
    run2 = p.add_run(codigo)
    run2.font.size = Pt(10)
    run2.font.name = "Consolas"

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


# ============================================================
# INFORME DE PROGRESO (PDF)
# ============================================================
def generar_pdf_progreso(user):
    """Genera un informe de progreso completo en PDF."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor, white
    from io import BytesIO

    # Datos
    user_score, _ = UserScore.objects.get_or_create(user=user)
    streak, _ = UserStreak.objects.get_or_create(user=user)
    inscripciones = Inscripcion.objects.filter(user=user).select_related('course')
    certificados = Certificado.objects.filter(usuario=user)
    logros = Logro.objects.filter(user=user)
    progreso_qs = UserProgress.objects.filter(user=user, completed=True)

    buffer = BytesIO()
    W, H = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    dorado = HexColor("#C9A227")
    azul = HexColor("#0a0e27")
    cyan = HexColor("#00d4ff")
    gris = HexColor("#888888")
    verde = HexColor("#00ff88")

    # Fondo
    c.setFillColor(azul)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Encabezado
    c.setFillColor(cyan)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, H-50, "⌛ ARCHIVO DE VECTOR")
    c.setFillColor(gris)
    c.setFont("Helvetica", 9)
    c.drawString(40, H-65, "Informe de progreso académico")

    # Datos del estudiante
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, H-100, user.get_full_name() or user.username)
    c.setFillColor(gris)
    c.setFont("Helvetica", 10)
    c.drawString(40, H-118, f"Usuario: {user.username} · Email: {user.email or '—'}")
    from datetime import datetime
    c.drawString(40, H-132, f"Informe generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Separador
    c.setStrokeColor(dorado)
    c.setLineWidth(1)
    c.line(40, H-145, W-40, H-145)

    # Estadísticas
    y = H-180
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "📊 RESUMEN")
    y -= 25

    stats = [
        ("🏆 Puntos totales", str(user_score.total_points)),
        ("🔥 Racha actual", f"{streak.current_streak} días"),
        ("📚 Lecciones completadas", str(progreso_qs.count())),
        ("📖 Cursos inscritos", str(inscripciones.count())),
        ("🏅 Logros obtenidos", str(logros.count())),
        ("🎓 Certificados", str(certificados.count())),
    ]

    for label, value in stats:
        c.setFillColor(gris)
        c.setFont("Helvetica", 10)
        c.drawString(50, y, label)
        c.setFillColor(cyan)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(300, y, value)
        y -= 18

    # Cursos
    y -= 20
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "📖 PROGRESO POR CURSO")
    y -= 20

    for insc in inscripciones:
        course = insc.course
        total = course.lessons.count()
        completadas = progreso_qs.filter(lesson__course=course).count()
        pct = round((completadas / total * 100) if total > 0 else 0)

        if y < 80:
            c.showPage()
            c.setFillColor(azul)
            c.rect(0, 0, W, H, fill=1, stroke=0)
            y = H - 60

        c.setFillColor(white)
        c.setFont("Helvetica", 9)
        c.drawString(50, y, course.name[:55])

        # Barra
        bar_x = 350
        bar_w = 150
        bar_h = 8
        c.setFillColor(HexColor("#2a2a3e"))
        c.rect(bar_x, y-2, bar_w, bar_h, fill=1, stroke=0)
        c.setFillColor(verde if pct == 100 else cyan)
        c.rect(bar_x, y-2, bar_w * pct / 100, bar_h, fill=1, stroke=0)

        c.setFillColor(gris)
        c.setFont("Helvetica", 8)
        c.drawString(bar_x + bar_w + 10, y, f"{completadas}/{total} ({pct}%)")

        y -= 15

    # Pie
    c.setFillColor(gris)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W/2, 30, "Archivo de Vector · Informe generado automáticamente")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


@login_required
def descargar_certificado_pdf(request, curso_slug):
    """Descarga certificado PDF mejorado."""
    curso = get_object_or_404(Course, slug=curso_slug, is_active=True)
    lecciones = curso.lessons.filter(is_active=True)
    total_ejercicios = sum(l.exercises.count() for l in lecciones)
    completados = UserProgress.objects.filter(user=request.user, lesson__course=curso, completed=True).count()
    puntuacion = UserProgress.objects.filter(user=request.user, lesson__course=curso).aggregate(total=models.Sum('score'))['total'] or 0
    porcentaje = int((completados / total_ejercicios * 100)) if total_ejercicios > 0 else 0

    from core.models import Certificado
    from core.certificados import generar_pdf_certificado as _pdf_cert_nuevo
    cert, created = Certificado.objects.get_or_create(
        usuario=request.user, curso=curso, leccion=None,
        defaults={
            'titulo': f"Curso: {curso.name}",
            'puntuacion': puntuacion,
            'ejercicios_completados': completados,
            'total_ejercicios': total_ejercicios,
            'porcentaje': porcentaje,
            'codigo_verificacion': f"VECTOR-{uuid.uuid4().hex[:8].upper()}",
        }
    )

    from core.certificados import generar_pdf_certificado as _pdf_nuevo
    pdf = _pdf_nuevo(
        user=request.user,
        curso=curso,
        completados=completados,
        total=total_ejercicios,
        porcentaje=porcentaje,
        puntuacion=puntuacion,
        codigo=cert.codigo_verificacion,
        fecha=cert.fecha_emision,
    )

    response = HttpResponse(pdf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificado_{curso.slug}.pdf"'
    return response


@login_required
def descargar_certificado_docx(request, curso_slug):
    """Descarga certificado Word."""
    curso = get_object_or_404(Course, slug=curso_slug, is_active=True)
    lecciones = curso.lessons.filter(is_active=True)
    total_ejercicios = sum(l.exercises.count() for l in lecciones)
    completados = UserProgress.objects.filter(user=request.user, lesson__course=curso, completed=True).count()
    puntuacion = UserProgress.objects.filter(user=request.user, lesson__course=curso).aggregate(total=models.Sum('score'))['total'] or 0
    porcentaje = int((completados / total_ejercicios * 100)) if total_ejercicios > 0 else 0

    from core.models import Certificado
    from core.certificados import generar_pdf_certificado as _pdf_cert_nuevo
    cert, created = Certificado.objects.get_or_create(
        usuario=request.user, curso=curso, leccion=None,
        defaults={
            'titulo': f"Curso: {curso.name}",
            'puntuacion': puntuacion,
            'ejercicios_completados': completados,
            'total_ejercicios': total_ejercicios,
            'porcentaje': porcentaje,
            'codigo_verificacion': f"VECTOR-{uuid.uuid4().hex[:8].upper()}",
        }
    )

    try:
        docx = generar_docx_certificado(
            user=request.user,
            titulo=f"Curso: {curso.name}",
            curso=curso,
            completados=completados,
            total_ejercicios=total_ejercicios,
            porcentaje=porcentaje,
            puntuacion=puntuacion,
            codigo=cert.codigo_verificacion,
            fecha=cert.fecha_emision,
        )
    except ImportError as e:
        return HttpResponse(f"Error: {e}. Instala python-docx.", status=500)

    response = HttpResponse(
        docx.read(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="certificado_{curso.slug}.docx"'
    return response


@login_required
def descargar_informe_progreso(request, formato='pdf'):
    """Descarga informe de progreso."""
    pdf = generar_pdf_progreso(request.user)
    response = HttpResponse(pdf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="progreso_{request.user.username}.pdf"'
    return response


# ============================================================
# VISTAS DEL PROFESOR (dashboard, estudiantes, evaluar, certificar)
# ============================================================

@staff_member_required
def teacher_dashboard(request):
    """Dashboard del profesor: sus cursos + estadisticas."""
    mis_cursos = Course.objects.filter(teachers=request.user, is_active=True)
    if not mis_cursos.exists():
        # Fallback: si no tiene cursos asignados, mostrar todos (modo admin)
        mis_cursos = Course.objects.filter(is_active=True)

    cursos_data = []
    total_estudiantes = set()
    total_inscripciones = 0
    total_certs = 0

    for curso in mis_cursos:
        inscripciones = Inscripcion.objects.filter(course=curso)
        n_est = inscripciones.count()
        estudiantes_ids = list(inscripciones.values_list('user_id', flat=True))
        total_estudiantes.update(estudiantes_ids)
        total_inscripciones += n_est

        certs = Certificado.objects.filter(curso=curso).count()
        total_certs += certs

        # Progreso promedio
        total_lecciones = curso.lessons.count()
        total_completadas = UserProgress.objects.filter(
            user_id__in=estudiantes_ids, lesson__course=curso, completed=True
        ).count()
        promedio = round((total_completadas / (total_lecciones * n_est) * 100)) if total_lecciones and n_est else 0

        cursos_data.append({
            'curso': curso,
            'estudiantes': n_est,
            'certificados': certs,
            'promedio': promedio,
            'total_lecciones': total_lecciones,
        })

    context = {
        'cursos_data': cursos_data,
        'total_cursos': mis_cursos.count(),
        'total_estudiantes': len(total_estudiantes),
        'total_inscripciones': total_inscripciones,
        'total_certificados': total_certs,
    }
    return render(request, 'core/teacher_dashboard.html', context)


@staff_member_required
def teacher_course_students(request, curso_slug):
    """Lista de estudiantes inscritos en un curso con su progreso."""
    curso = get_object_or_404(Course, slug=curso_slug, is_active=True)
    inscripciones = Inscripcion.objects.filter(course=curso).select_related('user')

    total_lecciones = curso.lessons.count()
    estudiantes_data = []

    for insc in inscripciones:
        user = insc.user
        progreso = UserProgress.objects.filter(
            user=user, lesson__course=curso, completed=True
        ).count()
        porcentaje = round((progreso / total_lecciones * 100)) if total_lecciones else 0
        score = UserScore.objects.filter(user=user).first()
        cert = Certificado.objects.filter(usuario=user, curso=curso).first()
        eval_obj = Evaluacion.objects.filter(estudiante=user, curso=curso).first()

        estudiantes_data.append({
            'user': user,
            'progreso': progreso,
            'total_lecciones': total_lecciones,
            'porcentaje': porcentaje,
            'puntos': score.total_points if score else 0,
            'certificado': cert,
            'evaluacion': eval_obj,
        })

    # Ordenar por porcentaje desc
    estudiantes_data.sort(key=lambda x: -x['porcentaje'])

    context = {
        'curso': curso,
        'estudiantes_data': estudiantes_data,
        'total_estudiantes': len(estudiantes_data),
    }
    return render(request, 'core/teacher_course_students.html', context)


@staff_member_required
def teacher_student_detail(request, curso_slug, user_id):
    """Detalle de un estudiante en un curso."""
    curso = get_object_or_404(Course, slug=curso_slug, is_active=True)
    estudiante = get_object_or_404(User, id=user_id)

    lecciones = curso.lessons.all().order_by('order')
    lecciones_data = []
    for lec in lecciones:
        prog = UserProgress.objects.filter(user=estudiante, lesson=lec).first()
        lecciones_data.append({
            'leccion': lec,
            'progreso': prog,
            'completada': prog.completed if prog else False,
            'score': prog.score if prog else 0,
        })

    total = len(lecciones_data)
    completadas = sum(1 for l in lecciones_data if l['completada'])
    porcentaje = round((completadas / total * 100)) if total else 0

    cert = Certificado.objects.filter(usuario=estudiante, curso=curso).first()
    eval_obj = Evaluacion.objects.filter(estudiante=estudiante, curso=curso).first()

    context = {
        'curso': curso,
        'estudiante': estudiante,
        'lecciones_data': lecciones_data,
        'total': total,
        'completadas': completadas,
        'porcentaje': porcentaje,
        'certificado': cert,
        'evaluacion': eval_obj,
    }
    return render(request, 'core/teacher_student_detail.html', context)


@staff_member_required
def teacher_evaluate(request, curso_slug, user_id):
    """Formulario para evaluar a un estudiante."""
    curso = get_object_or_404(Course, slug=curso_slug, is_active=True)
    estudiante = get_object_or_404(User, id=user_id)

    evaluacion = Evaluacion.objects.filter(
        profesor=request.user, estudiante=estudiante, curso=curso
    ).first()

    if request.method == 'POST':
        nota = int(request.POST.get('nota', 0))
        comentario = request.POST.get('comentario', '')

        if evaluacion:
            evaluacion.nota = nota
            evaluacion.comentario = comentario
            evaluacion.save()
        else:
            Evaluacion.objects.create(
                profesor=request.user,
                estudiante=estudiante,
                curso=curso,
                nota=nota,
                comentario=comentario,
            )

        crear_notificacion_evaluacion(estudiante, curso, nota, request.user)
        return redirect('teacher_course_students', curso_slug=curso.slug)

    context = {
        'curso': curso,
        'estudiante': estudiante,
        'evaluacion': evaluacion,
    }
    return render(request, 'core/teacher_evaluate.html', context)


@staff_member_required
def teacher_certify(request, curso_slug, user_id):
    """Emite certificado manualmente para un estudiante."""
    curso = get_object_or_404(Course, slug=curso_slug, is_active=True)
    estudiante = get_object_or_404(User, id=user_id)

    lecciones = curso.lessons.filter(is_active=True)
    total_ejercicios = sum(l.exercises.count() for l in lecciones)
    completados = UserProgress.objects.filter(
        user=estudiante, lesson__course=curso, completed=True
    ).count()
    puntuacion = UserProgress.objects.filter(
        user=estudiante, lesson__course=curso
    ).aggregate(total=models.Sum('score'))['total'] or 0
    porcentaje = int((completados / total_ejercicios * 100)) if total_ejercicios > 0 else 0

    cert, created = Certificado.objects.get_or_create(
        usuario=estudiante,
        curso=curso,
        leccion=None,
        defaults={
            'titulo': 'Curso: ' + curso.name,
            'puntuacion': puntuacion,
            'ejercicios_completados': completados,
            'total_ejercicios': total_ejercicios,
            'porcentaje': porcentaje,
            'codigo_verificacion': 'VECTOR-' + uuid.uuid4().hex[:8].upper(),
        }
    )

    return redirect('teacher_course_students', curso_slug=curso.slug)


@staff_member_required
def teacher_student_progress_pdf(request, curso_slug, user_id):
    """PDF con el progreso de un estudiante en un curso."""
    curso = get_object_or_404(Course, slug=curso_slug, is_active=True)
    estudiante = get_object_or_404(User, id=user_id)

    pdf = generar_pdf_progreso(estudiante)

    response = HttpResponse(pdf.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="progreso_' + estudiante.username + '.pdf"'
    return response


# ============================================================
# CRUD DE CURSOS Y LECCIONES (profesor)
# ============================================================

@staff_member_required
def teacher_course_edit(request, curso_slug=None):
    curso = None
    if curso_slug:
        curso = get_object_or_404(Course, slug=curso_slug)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip() or name.lower().replace(' ', '-')
        description = request.POST.get('description', '')
        icon = request.POST.get('icon', '📚')
        category = request.POST.get('category', 'general')
        order = int(request.POST.get('order', 0))
        is_active = request.POST.get('is_active') == 'on'

        if curso:
            curso.name = name
            curso.slug = slug
            curso.description = description
            curso.icon = icon
            curso.category = category
            curso.order = order
            curso.is_active = is_active
            curso.save()
        else:
            curso = Course.objects.create(
                name=name, slug=slug, description=description,
                icon=icon, category=category, order=order, is_active=is_active,
            )
            curso.teachers.add(request.user)

        return redirect('teacher_course_students', curso_slug=curso.slug)

    context = {
        'curso': curso,
        'categorias': Course.CATEGORY_CHOICES,
        'accion': 'Editar' if curso else 'Crear',
    }
    return render(request, 'core/teacher_course_edit.html', context)


@staff_member_required
def teacher_course_delete(request, curso_slug):
    curso = get_object_or_404(Course, slug=curso_slug)
    if request.method == 'POST':
        curso.delete()
        return redirect('teacher_dashboard')
    return render(request, 'core/teacher_confirm_delete.html', {
        'objeto': curso,
        'tipo': 'curso',
    })


@staff_member_required
def teacher_course_lessons(request, curso_slug):
    curso = get_object_or_404(Course, slug=curso_slug)
    lecciones = curso.lessons.all().order_by('order')
    return render(request, 'core/teacher_course_lessons.html', {
        'curso': curso,
        'lecciones': lecciones,
    })


@staff_member_required
def teacher_lesson_edit(request, curso_slug, lesson_id=None):
    curso = get_object_or_404(Course, slug=curso_slug)
    leccion = None
    if lesson_id:
        leccion = get_object_or_404(Lesson, id=lesson_id, course=curso)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '')
        order = int(request.POST.get('order', 0))
        difficulty = request.POST.get('difficulty', 'beginner')
        is_active = request.POST.get('is_active') == 'on'

        if leccion:
            leccion.title = title
            leccion.content = content
            leccion.order = order
            leccion.difficulty = difficulty
            leccion.is_active = is_active
            leccion.save()
        else:
            leccion = Lesson.objects.create(
                course=curso, title=title, content=content,
                order=order, difficulty=difficulty, is_active=is_active,
            )

        return redirect('teacher_lesson_detail', lesson_id=leccion.id)

    dificultades = getattr(Lesson, 'DIFFICULTY_CHOICES', [
        ('beginner', 'Principiante'), ('intermediate', 'Intermedio'), ('advanced', 'Avanzado')
    ])
    context = {
        'curso': curso,
        'leccion': leccion,
        'dificultades': dificultades,
        'accion': 'Editar' if leccion else 'Crear',
    }
    return render(request, 'core/teacher_lesson_edit.html', context)


@staff_member_required
def teacher_lesson_delete(request, curso_slug, lesson_id):
    curso = get_object_or_404(Course, slug=curso_slug)
    leccion = get_object_or_404(Lesson, id=lesson_id, course=curso)
    if request.method == 'POST':
        leccion.delete()
        return redirect('teacher_course_lessons', curso_slug=curso.slug)
    return render(request, 'core/teacher_confirm_delete.html', {
        'objeto': leccion,
        'tipo': 'leccion',
        'curso': curso,
    })


# ============================================================
# NOTIFICACIONES
# ============================================================

@login_required
def notificaciones_lista(request):
    """Lista de notificaciones del usuario."""
    from core.models import Notificacion
    notifs = Notificacion.objects.filter(user=request.user)
    no_leidas = notifs.filter(leida=False).count()
    return render(request, 'core/notificaciones.html', {
        'notificaciones': notifs,
        'no_leidas': no_leidas,
    })


@login_required
def notificacion_leer(request, notif_id):
    """Marca una notificacion como leida y redirige a su URL."""
    from core.models import Notificacion
    from django.shortcuts import redirect as _redir
    notif = get_object_or_404(Notificacion, id=notif_id, user=request.user)
    notif.leida = True
    notif.save()
    if notif.url:
        return _redir(notif.url)
    return _redir('notificaciones_lista')


@login_required
def notificaciones_marcar_todas(request):
    """Marca todas las notificaciones como leidas."""
    from core.models import Notificacion
    from django.shortcuts import redirect as _redir
    Notificacion.objects.filter(user=request.user, leida=False).update(leida=True)
    return _redir('notificaciones_lista')


# ============================================================
# RANKING DE ESTUDIANTES
# ============================================================

def _medalla(pos):
    if pos == 1: return "🥇"
    if pos == 2: return "🥈"
    if pos == 3: return "🥉"
    return ""


def _calcular_ranking_curso(curso):
    """Devuelve lista ordenada de estudiantes por puntos en un curso."""
    from django.db.models import Sum
    inscripciones = Inscripcion.objects.filter(course=curso).select_related('user')
    total_lecciones = curso.lessons.count()

    datos = []
    for insc in inscripciones:
        user = insc.user
        progs = UserProgress.objects.filter(user=user, lesson__course=curso, completed=True)
        completadas = progs.count()
        puntos = progs.aggregate(t=Sum('score'))['t'] or 0
        porcentaje = round((completadas / total_lecciones * 100)) if total_lecciones else 0
        cert = Certificado.objects.filter(usuario=user, curso=curso).exists()
        eval_obj = Evaluacion.objects.filter(estudiante=user, curso=curso).first()

        datos.append({
            'user': user,
            'puntos': puntos,
            'completadas': completadas,
            'total': total_lecciones,
            'porcentaje': porcentaje,
            'certificado': cert,
            'nota': eval_obj.nota if eval_obj else None,
        })

    datos.sort(key=lambda x: (-x['puntos'], -x['porcentaje']))
    for i, d in enumerate(datos, 1):
        d['posicion'] = i
        d['medalla'] = _medalla(i)
    return datos


def _calcular_ranking_global():
    """Top estudiantes de toda la plataforma."""
    from django.db.models import Sum
    scores = UserScore.objects.select_related('user').order_by('-total_points')[:50]
    datos = []
    for i, s in enumerate(scores, 1):
        datos.append({
            'user': s.user,
            'puntos': s.total_points,
            'lecciones': s.lessons_completed,
            'posicion': i,
            'medalla': _medalla(i),
        })
    return datos


def ranking_curso(request, curso_slug):
    """Ranking de estudiantes de un curso."""
    curso = get_object_or_404(Course, slug=curso_slug, is_active=True)
    ranking = _calcular_ranking_curso(curso)

    # Posicion del usuario actual si esta logueado
    mi_posicion = None
    if request.user.is_authenticated:
        for d in ranking:
            if d['user'].id == request.user.id:
                mi_posicion = d
                break

    return render(request, 'core/ranking_curso.html', {
        'curso': curso,
        'ranking': ranking,
        'mi_posicion': mi_posicion,
        'total': len(ranking),
    })


def ranking_global(request):
    """Ranking global de estudiantes."""
    ranking = _calcular_ranking_global()

    mi_posicion = None
    if request.user.is_authenticated:
        for d in ranking:
            if d['user'].id == request.user.id:
                mi_posicion = d
                break

    return render(request, 'core/ranking_global.html', {
        'ranking': ranking,
        'mi_posicion': mi_posicion,
    })


@staff_member_required
def ranking_profesor(request):
    """Ranking de los cursos del profesor."""
    mis_cursos = Course.objects.filter(teachers=request.user, is_active=True)
    if not mis_cursos.exists():
        mis_cursos = Course.objects.filter(is_active=True)

    cursos_ranking = []
    for curso in mis_cursos:
        top = _calcular_ranking_curso(curso)[:5]
        cursos_ranking.append({
            'curso': curso,
            'top': top,
            'total': Inscripcion.objects.filter(course=curso).count(),
        })

    return render(request, 'core/ranking_profesor.html', {
        'cursos_ranking': cursos_ranking,
    })


# ============================================================
# BUSCADOR CON FILTROS
# ============================================================

def buscar(request):
    """Buscador global con filtros."""
    from django.db.models import Q

    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    dificultad = request.GET.get('dificultad', '').strip()
    tipo = request.GET.get('tipo', 'todo').strip()

    cursos = Course.objects.none()
    lecciones = Lesson.objects.none()

    if q or categoria or dificultad:
        # Cursos
        if tipo in ('todo', 'cursos'):
            cursos = Course.objects.filter(is_active=True)
            if q:
                cursos = cursos.filter(
                    Q(name__icontains=q) | Q(description__icontains=q)
                )
            if categoria:
                cursos = cursos.filter(category=categoria)
            cursos = cursos.order_by('order', 'name')[:30]

        # Lecciones
        if tipo in ('todo', 'lecciones'):
            lecciones = Lesson.objects.filter(is_active=True).select_related('course')
            if q:
                lecciones = lecciones.filter(
                    Q(title__icontains=q) | Q(meaning__icontains=q) |
                    Q(example__icontains=q) | Q(breakdown__icontains=q) |
                    Q(course__name__icontains=q)
                )
            if dificultad:
                lecciones = lecciones.filter(difficulty=dificultad)
            if categoria:
                lecciones = lecciones.filter(course__category=categoria)
            lecciones = lecciones.order_by('course__name', 'order')[:50]

    total = cursos.count() + lecciones.count()

    context = {
        'q': q,
        'categoria': categoria,
        'dificultad': dificultad,
        'tipo': tipo,
        'cursos': cursos,
        'lecciones': lecciones,
        'total': total,
        'categorias': Course.CATEGORY_CHOICES,
        'dificultades': getattr(Lesson, 'DIFFICULTY_CHOICES', [
            ('beginner', 'Principiante'),
            ('intermediate', 'Intermedio'),
            ('advanced', 'Avanzado'),
        ]),
        'hay_filtros': bool(q or categoria or dificultad),
    }
    return render(request, 'core/buscar.html', context)
