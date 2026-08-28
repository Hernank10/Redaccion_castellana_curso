from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('curso/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('api/leccion/<slug:course_slug>/<int:lesson_order>/', views.get_lesson_data, name='get_lesson_data'),
    path('api/guardar-progreso/', views.save_lesson_progress, name='save_progress'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
