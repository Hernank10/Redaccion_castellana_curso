from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLES = (
        ('student', 'Estudiante'),
        ('teacher', 'Profesor'),
        ('admin', 'Administrador'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLES, default='student')
    bio = models.TextField(blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    birth_date = models.DateField(null=True, blank=True)
    institution = models.CharField(max_length=200, blank=True, default='')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class Course(models.Model):
    CATEGORY_CHOICES = (
        ('etymology', 'Raíces y Etimología'),
        ('periphrasis', 'Perífrasis Verbales'),
        ('phonetics', 'Fonética y AFI'),
        ('punctuation', 'Signos de Puntuación'),
        ('connectors', 'Conectores y Cohesión'),
        ('rhetoric', 'Figuras Retóricas'),
        ('comparison', 'Fórmulas de Comparación'),
        ('description', 'Fórmulas de Descripción'),
        ('exposition', 'Fórmulas de Exposición'),
        ('argumentation', 'Fórmulas de Argumentación'),
        ('narration', 'Fórmulas de Narración'),
        ('grammar', 'Gramática del Castellano'),
        ('syntax', 'Sintaxis del Castellano'),
        ('literature', 'Literatura Hispanoamericana'),
        ('poetry', 'Poesía Castellana'),
        ('orthography', 'Ortografía Castellana'),
        ('writing', 'Redacción Avanzada'),
        ('communication', 'Comunicación Escrita'),
        ('academic', 'Redacción Académica'),
        ('scientific', 'Redacción Científica'),
        ('journalism', 'Redacción Periodística'),
    )
    slug = models.SlugField(unique=True, max_length=50)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, default='📚')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, default='general')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    teachers = models.ManyToManyField(User, related_name='courses_taught', blank=True)
    
    def __str__(self):
        return self.name

class Lesson(models.Model):
    DIFFICULTY_CHOICES = (
        ('beginner', 'Principiante'),
        ('intermediate', 'Intermedio'),
        ('advanced', 'Avanzado'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    root = models.CharField(max_length=200)
    meaning = models.TextField()
    example = models.TextField(blank=True, default='')
    breakdown = models.TextField(blank=True, default='')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate')
    duration_minutes = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.name} - {self.order}: {self.title[:50]}"

class Exercise(models.Model):
    EXERCISE_TYPES = (
        ('multiple_choice', 'Opción Múltiple'),
        ('true_false', 'Verdadero/Falso'),
        ('fill_blank', 'Completar'),
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES, default='multiple_choice')
    question = models.TextField()
    option_a = models.CharField(max_length=500, blank=True, default='')
    option_b = models.CharField(max_length=500, blank=True, default='')
    option_c = models.CharField(max_length=500, blank=True, default='')
    option_d = models.CharField(max_length=500, blank=True, default='')
    correct_answer = models.CharField(max_length=10, blank=True, default='')
    explanation = models.TextField(blank=True, default='')
    points = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)
    attempts = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'lesson']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title[:30]}"

class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    max_streak = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}: racha {self.current_streak}"

class UserScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='score')
    total_points = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}: {self.total_points} pts"

class Certificado(models.Model):
    """Modelo para almacenar certificados generados"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificados')
    curso = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='certificados', null=True, blank=True)
    leccion = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='certificados', null=True, blank=True)
    titulo = models.CharField(max_length=200)
    puntuacion = models.PositiveIntegerField(default=0)
    ejercicios_completados = models.PositiveIntegerField(default=0)
    total_ejercicios = models.PositiveIntegerField(default=0)
    porcentaje = models.PositiveIntegerField(default=0)
    codigo_verificacion = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    archivo_pdf = models.FileField(upload_to='certificados/', blank=True, null=True)
    
    def __str__(self):
        return f"Certificado de {self.usuario.username} - {self.titulo[:30]}"
    
    class Meta:
        ordering = ['-fecha_emision']
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'
class Inscripcion(models.Model):
    """Curso al que se ha inscrito un usuario."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscripciones')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='inscripciones')
    fecha = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'

    def __str__(self):
        return f"{self.user.username} → {self.course.name}"


class Logro(models.Model):
    """Insignia o medalla desbloqueada por un usuario."""
    TIPOS = [
        ('insignia', 'Insignia'),
        ('medalla', 'Medalla'),
        ('estrella', 'Estrella'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logros')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='insignia')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=10, default='🏅')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Logro'
        verbose_name_plural = 'Logros'

    def __str__(self):
        return f"{self.user.username} - {self.nombre}"

# ============================================================
# MODELOS AÑADIDOS: Inscripcion + Logro
# ============================================================


class Evaluacion(models.Model):
    """Evaluacion de un profesor a un estudiante en un curso."""
    profesor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluaciones_dadas')
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluaciones_recibidas')
    curso = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='evaluaciones')
    nota = models.PositiveIntegerField(default=0)
    comentario = models.TextField(blank=True, default='')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profesor', 'estudiante', 'curso')
        verbose_name = 'Evaluacion'
        verbose_name_plural = 'Evaluaciones'

    def __str__(self):
        return self.estudiante.username + ' - ' + self.curso.name + ' (' + str(self.nota) + ')'


class Notificacion(models.Model):
    """Notificacion para un usuario."""
    TIPOS = [
        ('curso_completado', 'Curso completado'),
        ('evaluacion', 'Evaluacion recibida'),
        ('certificado', 'Certificado emitido'),
        ('logro', 'Logro desbloqueado'),
        ('inscripcion', 'Nueva inscripcion'),
        ('info', 'Informacion'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=30, choices=TIPOS, default='info')
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField(blank=True, default='')
    url = models.CharField(max_length=300, blank=True, default='')
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Notificacion'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return self.user.username + ' - ' + self.titulo
