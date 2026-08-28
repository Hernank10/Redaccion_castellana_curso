from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    CATEGORY_CHOICES = [
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
    ]
    slug = models.SlugField(unique=True, max_length=50)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, default='📚')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, default='general')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order']

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    root = models.CharField(max_length=200)
    meaning = models.TextField()
    example = models.TextField(blank=True, default='')
    breakdown = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.name} - {self.order}: {self.title[:50]}"

class Exercise(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    question = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    
    def __str__(self):
        return f"Ejercicio para {self.lesson.title[:30]}"

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)
    attempts = models.PositiveIntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'lesson']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title[:30]}"

class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    max_streak = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}: racha {self.current_streak}"

class UserScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='score')
    total_points = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}: {self.total_points} pts"
