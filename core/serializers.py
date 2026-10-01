# -*- coding: utf-8 -*-
"""serializers.py - Serializers de la API."""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Course, Lesson, Exercise, UserProgress, UserScore,
    UserStreak, Certificado, Inscripcion, Logro, Evaluacion,
    Notificacion, Profile,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'is_staff']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    exercises_count = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'order', 'difficulty', 'is_active', 'exercises_count']

    def get_exercises_count(self, obj):
        return obj.exercises.count()


class CourseSerializer(serializers.ModelSerializer):
    teachers = UserSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'slug', 'name', 'description', 'icon', 'category',
                  'category_display', 'order', 'is_active', 'teachers', 'lessons_count']

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseDetailSerializer(CourseSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['lessons']


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'lesson', 'exercise_type', 'question',
                  'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        extra_kwargs = {'correct_answer': {'write_only': True}}


class UserProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_name = serializers.CharField(source='lesson.course.name', read_only=True)

    class Meta:
        model = UserProgress
        fields = ['id', 'user', 'lesson', 'lesson_title', 'course_name',
                  'completed', 'score', 'attempts']
        read_only_fields = ['user']


class UserScoreSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserScore
        fields = ['username', 'total_points', 'lessons_completed']


class UserStreakSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserStreak
        fields = ['username', 'current_streak', 'last_activity']


class CertificadoSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.CharField(source='curso.name', read_only=True)
    estudiante = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Certificado
        fields = ['id', 'estudiante', 'curso', 'curso_nombre', 'titulo',
                  'codigo_verificacion', 'porcentaje', 'puntuacion', 'fecha_emision']
        read_only_fields = ['codigo_verificacion', 'fecha_emision']


class InscripcionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Inscripcion
        fields = ['id', 'user', 'username', 'course', 'course_name', 'course_slug',
                  'fecha', 'completado']
        read_only_fields = ['user', 'fecha']


class LogroSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Logro
        fields = ['id', 'username', 'tipo', 'nombre', 'descripcion', 'icono', 'fecha']
        read_only_fields = ['fecha']


class EvaluacionSerializer(serializers.ModelSerializer):
    profesor_username = serializers.CharField(source='profesor.username', read_only=True)
    estudiante_username = serializers.CharField(source='estudiante.username', read_only=True)
    curso_nombre = serializers.CharField(source='curso.name', read_only=True)

    class Meta:
        model = Evaluacion
        fields = ['id', 'profesor', 'profesor_username', 'estudiante',
                  'estudiante_username', 'curso', 'curso_nombre',
                  'nota', 'comentario', 'fecha']
        read_only_fields = ['profesor', 'fecha']


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'tipo', 'titulo', 'mensaje', 'url', 'leida', 'fecha']
        read_only_fields = ['fecha']


class RankingItemSerializer(serializers.Serializer):
    posicion = serializers.IntegerField()
    username = serializers.CharField()
    puntos = serializers.IntegerField()
    lecciones = serializers.IntegerField()