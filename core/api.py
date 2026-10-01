# -*- coding: utf-8 -*-
"""api.py - Vistas de la API REST."""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404

from .models import (
    Course, Lesson, Exercise, UserProgress, UserScore, UserStreak,
    Certificado, Inscripcion, Logro, Evaluacion, Notificacion,
)
from .serializers import (
    UserSerializer, UserRegisterSerializer, ProfileSerializer,
    CourseSerializer, CourseDetailSerializer, LessonSerializer,
    ExerciseSerializer, UserProgressSerializer, UserScoreSerializer,
    UserStreakSerializer, CertificadoSerializer, InscripcionSerializer,
    LogroSerializer, EvaluacionSerializer, NotificacionSerializer,
)


# ============================================================
# AUTH
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """Registrar usuario nuevo y devolver token."""
    s = UserRegisterSerializer(data=request.data)
    if s.is_valid():
        user = s.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """Login con username/password, devuelve token."""
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Credenciales invalidas'}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """Cerrar sesion (borra token)."""
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'ok': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_me(request):
    """Datos del usuario actual + stats."""
    user = request.user
    score, _ = UserScore.objects.get_or_create(user=user)
    streak, _ = UserStreak.objects.get_or_create(user=user)
    inscripciones = Inscripcion.objects.filter(user=user).count()
    certificados = Certificado.objects.filter(usuario=user).count()
    logros = Logro.objects.filter(user=user).count()

    return Response({
        'user': UserSerializer(user).data,
        'score': UserScoreSerializer(score).data,
        'streak': UserStreakSerializer(streak).data,
        'inscripciones': inscripciones,
        'certificados': certificados,
        'logros': logros,
    })


# ============================================================
# CURSOS Y LECCIONES
# ============================================================

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

    @action(detail=True, methods=['get'])
    def lessons(self, request, slug=None):
        curso = self.get_object()
        lecciones = curso.lessons.filter(is_active=True).order_by('order')
        return Response(LessonSerializer(lecciones, many=True).data)

    @action(detail=True, methods=['get'])
    def ranking(self, request, slug=None):
        """Top 20 estudiantes del curso."""
        curso = self.get_object()
        inscripciones = Inscripcion.objects.filter(course=curso).select_related('user')
        datos = []
        for insc in inscripciones:
            progs = UserProgress.objects.filter(user=insc.user, lesson__course=curso, completed=True)
            puntos = progs.aggregate(t=Sum('score'))['t'] or 0
            datos.append({
                'username': insc.user.username,
                'puntos': puntos,
                'lecciones': progs.count(),
            })
        datos.sort(key=lambda x: -x['puntos'])
        for i, d in enumerate(datos[:20], 1):
            d['posicion'] = i
        return Response(datos[:20])


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.filter(is_active=True).select_related('course')
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

    @action(detail=True, methods=['get'])
    def exercises(self, request, pk=None):
        leccion = self.get_object()
        ejercicios = leccion.exercises.filter(is_active=True)
        return Response(ExerciseSerializer(ejercicios, many=True).data)


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exercise.objects.filter(is_active=True)
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# ============================================================
# PROGRESO DEL USUARIO
# ============================================================

class UserProgressViewSet(viewsets.ModelViewSet):
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user).select_related('lesson', 'lesson__course')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def guardar(self, request):
        """Guardar progreso de una leccion."""
        lesson_id = request.data.get('lesson_id')
        score = int(request.data.get('score', 0))
        completed = bool(request.data.get('completed', False))

        leccion = get_object_or_404(Lesson, id=lesson_id)
        prog, created = UserProgress.objects.get_or_create(
            user=request.user, lesson=leccion
        )
        prog.attempts += 1
        if score > prog.score:
            prog.score = score
        if completed:
            prog.completed = True
        prog.save()

        # Actualizar score total
        user_score, _ = UserScore.objects.get_or_create(user=request.user)
        user_score.total_points = UserProgress.objects.filter(
            user=request.user, completed=True
        ).aggregate(t=Sum('score'))['t'] or 0
        user_score.lessons_completed = UserProgress.objects.filter(
            user=request.user, completed=True
        ).count()
        user_score.save()

        return Response({
            'ok': True,
            'progreso': UserProgressSerializer(prog).data,
            'score_total': user_score.total_points,
        })


class InscripcionViewSet(viewsets.ModelViewSet):
    serializer_class = InscripcionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Inscripcion.objects.filter(user=self.request.user).select_related('course')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def inscribirse(self, request):
        """Inscribirse en un curso."""
        curso_slug = request.data.get('curso_slug')
        curso = get_object_or_404(Course, slug=curso_slug, is_active=True)
        insc, created = Inscripcion.objects.get_or_create(
            user=request.user, course=curso
        )
        return Response({
            'ok': True,
            'created': created,
            'inscripcion': InscripcionSerializer(insc).data,
        })


class CertificadoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CertificadoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Certificado.objects.filter(usuario=self.request.user).select_related('curso')


class LogroViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LogroSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Logro.objects.filter(user=self.request.user)


class NotificacionViewSet(viewsets.ModelViewSet):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notificacion.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def leer(self, request, pk=None):
        notif = self.get_object()
        notif.leida = True
        notif.save()
        return Response({'ok': True})

    @action(detail=False, methods=['post'])
    def leer_todas(self, request):
        Notificacion.objects.filter(user=request.user, leida=False).update(leida=True)
        return Response({'ok': True})


# ============================================================
# RANKING
# ============================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_ranking_global(request):
    """Top 50 estudiantes global."""
    top = UserScore.objects.select_related('user').order_by('-total_points')[:50]
    datos = []
    for i, s in enumerate(top, 1):
        datos.append({
            'posicion': i,
            'username': s.user.username,
            'puntos': s.total_points,
            'lecciones': s.lessons_completed,
        })
    return Response(datos)