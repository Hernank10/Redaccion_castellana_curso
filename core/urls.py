from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('cursos/', views.course_list, name='course_list'),
    path('recursos/', views.resource_list, name='resource_list'),
    path('curso/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('practicar/<int:lesson_id>/', views.practice_lesson, name='practice_lesson'),
    path('api/leccion/<slug:course_slug>/<int:lesson_order>/', views.get_lesson_data, name='get_lesson_data'),
    path('api/guardar-progreso/', views.save_lesson_progress, name='save_progress'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil, name='perfil'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='core/password_change.html', success_url='/es/perfil/'), name='password_change'),
    path('profesor/', views.teacher_dashboard, name='teacher_dashboard'),
    path('profesor/leccion/<int:lesson_id>/', views.teacher_lesson_detail, name='teacher_lesson_detail'),
    path('profesor/ejercicio/editar/<int:exercise_id>/', views.teacher_exercise_edit, name='teacher_exercise_edit'),
    path('profesor/ejercicio/nuevo/', views.teacher_exercise_edit, name='teacher_exercise_new'),
    path('profesor/ejercicio/eliminar/<int:exercise_id>/', views.teacher_exercise_delete, name='teacher_exercise_delete'),
    path('certificado/leccion/<int:leccion_id>/', views.generar_certificado, name='certificado_leccion'),
    path('certificado/curso/<slug:curso_slug>/', views.generar_certificado, name='certificado_curso'),
    path('certificado/pdf/<slug:curso_slug>/', views.descargar_certificado_pdf, name='certificado_pdf'),
    path('certificado/docx/<slug:curso_slug>/', views.descargar_certificado_docx, name='certificado_docx'),
    path('informe/progreso/', views.descargar_informe_progreso, name='informe_progreso'),
]
