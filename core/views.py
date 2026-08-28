from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Course, Lesson, UserProgress, UserScore, UserStreak
import json

def index(request):
    """Página principal con todos los cursos"""
    courses = Course.objects.filter(is_active=True)
    total_lessons = sum(c.lessons.count() for c in courses)
    
    return render(request, 'core/index.html', {
        'courses': courses,
        'total_lessons': total_lessons,
        'total_courses': courses.count(),
    })

def course_detail(request, course_slug):
    """Página de detalle de un curso"""
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    lessons = course.lessons.filter(is_active=True)
    
    # Progreso del usuario
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
    """API: Obtener datos de una lección"""
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
    """API: Guardar progreso de una lección"""
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
            
            # Actualizar puntuación total
            user_score, _ = UserScore.objects.get_or_create(user=request.user)
            user_score.total_points += score
            user_score.lessons_completed = UserProgress.objects.filter(
                user=request.user, completed=True
            ).count()
            user_score.save()
            
            # Actualizar racha
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
    """Panel de control del usuario"""
    user_score = UserScore.objects.get_or_create(user=request.user)[0]
    streak = UserStreak.objects.get_or_create(user=request.user)[0]
    progress_count = UserProgress.objects.filter(user=request.user, completed=True).count()
    
    # Progreso por curso
    course_progress = {}
    for course in Course.objects.filter(is_active=True):
        total = course.lessons.count()
        completed = UserProgress.objects.filter(
            user=request.user, lesson__course=course, completed=True
        ).count()
        course_progress[course.id] = {
            'name': course.name,
            'total': total,
            'completed': completed,
            'percentage': round((completed / total * 100) if total > 0 else 0),
        }
    
    return render(request, 'core/dashboard.html', {
        'user_score': user_score,
        'streak': streak,
        'progress_count': progress_count,
        'course_progress': course_progress,
    })
