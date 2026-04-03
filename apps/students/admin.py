from django.contrib import admin
from .models import Student, Grade, Stream, AcademicYear


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_editable = ('is_current',)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'order')
    list_editable = ('order',)


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'capacity', 'current_enrollment', 'is_full')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_full_name', 'grade', 'stream', 'status', 'enrollment_date')
    list_filter = ('status', 'grade', 'gender', 'academic_year')
    search_fields = ('first_name', 'last_name', 'student_id', 'guardian_name')
    readonly_fields = ('student_id', 'enrollment_date', 'created_at', 'updated_at')