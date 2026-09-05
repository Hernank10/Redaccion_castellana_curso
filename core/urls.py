from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('curso/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('practicar/<int:lesson_id>/', views.practice_lesson, name='practice_lesson'),
    path('api/leccion/<slug:course_slug>/<int:lesson_order>/', views.get_lesson_data, name='get_lesson_data'),
    path('api/guardar-progreso/', views.save_lesson_progress, name='save_progress'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profesor/', views.teacher_dashboard, name='teacher_dashboard'),
    path('profesor/leccion/<int:lesson_id>/', views.teacher_lesson_detail, name='teacher_lesson_detail'),
    path('profesor/ejercicio/editar/<int:exercise_id>/', views.teacher_exercise_edit, name='teacher_exercise_edit'),
    path('profesor/ejercicio/nuevo/', views.teacher_exercise_edit, name='teacher_exercise_new'),
    path('profesor/ejercicio/eliminar/<int:exercise_id>/', views.teacher_exercise_delete, name='teacher_exercise_delete'),
    path('certificado/leccion/<int:leccion_id>/', views.generar_certificado, name='certificado_leccion'),
    path('certificado/curso/<slug:curso_slug>/', views.generar_certificado, name='certificado_curso'),
]
