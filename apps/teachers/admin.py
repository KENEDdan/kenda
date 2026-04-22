from django.contrib import admin
from .models import Teacher, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'head')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        'teacher_id', 'get_full_name', 'department',
        'employment_type', 'status', 'join_date'
    )
    list_filter = ('status', 'gender', 'employment_type', 'department')
    search_fields = ('first_name', 'last_name', 'teacher_id', 'email')
    readonly_fields = ('teacher_id', 'join_date', 'created_at', 'updated_at')