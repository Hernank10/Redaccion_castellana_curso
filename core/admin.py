from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Profile, Course, Lesson, Exercise,
    UserProgress, UserScore, UserStreak
)

# ===== INLINE PARA EJERCICIOS (dentro de Lección) =====
class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 3
    fields = ('exercise_type', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'points', 'is_active')
    show_change_link = True

# ===== PERFIL DE USUARIO =====
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('role', 'bio', 'phone', 'birth_date', 'institution')

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_active', 'date_joined')
    list_filter = ('profile__role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'Sin rol'
    get_role.short_description = 'Rol'
    get_role.admin_order_field = 'profile__role'

# ===== REGISTROS =====
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'slug', 'category', 'lesson_count', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('teachers',)
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Lecciones'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    inlines = [ExerciseInline]
    list_display = ('title', 'course', 'order', 'difficulty', 'duration_minutes', 'is_active')
    list_filter = ('course', 'difficulty', 'is_active')
    search_fields = ('title', 'root', 'meaning')

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'exercise_type', 'question_preview', 'points', 'is_active')
    list_filter = ('exercise_type', 'is_active', 'lesson__course')
    search_fields = ('question', 'explanation')
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Pregunta'

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'score', 'attempts')
    list_filter = ('completed', 'lesson__course')
    search_fields = ('user__username', 'lesson__title')

@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak', 'max_streak')
    search_fields = ('user__username',)

@admin.register(UserScore)
class UserScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'lessons_completed')
    search_fields = ('user__username',)
