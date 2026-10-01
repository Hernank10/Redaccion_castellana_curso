# -*- coding: utf-8 -*-
"""urls_api.py - URLs de la API REST."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'courses', api.CourseViewSet, basename='api-course')
router.register(r'lessons', api.LessonViewSet, basename='api-lesson')
router.register(r'exercises', api.ExerciseViewSet, basename='api-exercise')
router.register(r'progress', api.UserProgressViewSet, basename='api-progress')
router.register(r'inscripciones', api.InscripcionViewSet, basename='api-inscripcion')
router.register(r'certificados', api.CertificadoViewSet, basename='api-certificado')
router.register(r'logros', api.LogroViewSet, basename='api-logro')
router.register(r'notificaciones', api.NotificacionViewSet, basename='api-notificacion')

urlpatterns = [
    path('auth/register/', api.api_register, name='api-register'),
    path('auth/login/', api.api_login, name='api-login'),
    path('auth/logout/', api.api_logout, name='api-logout'),
    path('auth/me/', api.api_me, name='api-me'),
    path('ranking/', api.api_ranking_global, name='api-ranking'),
    path('', include(router.urls)),
]