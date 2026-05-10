from django.contrib import admin
from .models import Subject, ClassRoom, SubjectAssignment, Term, AssessmentType, GradeEntry


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

    from .models import AssessmentType, GradeEntry

@admin.register(AssessmentType)
class AssessmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'weight', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(GradeEntry)
class GradeEntryAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'subject_assignment', 'assessment_type',
        'term', 'marks', 'max_marks'
    )
    list_filter = ('term', 'assessment_type')
    search_fields = (
        'student__first_name', 'student__last_name',
        'student__student_id'
    )