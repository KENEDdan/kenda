from django.contrib import admin
from .models import Subject, ClassRoom, SubjectAssignment, Term


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'subject_type', 'is_active')
    list_filter = ('subject_type', 'is_active')
    search_fields = ('name', 'code')
    list_editable = ('is_active',)


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'class_teacher', 'student_count',
        'capacity', 'room_number', 'is_active'
    )
    list_filter = ('academic_year', 'grade', 'is_active')
    search_fields = ('name', 'grade__name')


@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('subject', 'classroom', 'teacher', 'periods_per_week')
    list_filter = ('classroom__academic_year', 'classroom__grade')
    search_fields = ('subject__name', 'teacher__first_name', 'teacher__last_name')


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start_date', 'end_date', 'is_current')
    list_editable = ('is_current',)