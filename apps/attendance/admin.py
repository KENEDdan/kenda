from django.contrib import admin
from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'classroom', 'date', 'status', 'marked_by'
    )
    list_filter = ('status', 'date', 'classroom__grade')
    search_fields = (
        'student__first_name', 'student__last_name',
        'student__student_id'
    )
    date_hierarchy = 'date'