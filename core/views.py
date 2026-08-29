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
