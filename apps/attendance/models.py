from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.students.models import Student, AcademicYear
from apps.academics.models import ClassRoom, Term


class AttendanceRecord(models.Model):
    """Daily attendance record for a student in a class."""

    class Status(models.TextChoices):
        PRESENT = 'present', _('Present')
        ABSENT = 'absent', _('Absent')
        LATE = 'late', _('Late')
        EXCUSED = 'excused', _('Excused')

    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PRESENT
    )
    term = models.ForeignKey(
        Term, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='attendance_records'
    )
    notes = models.CharField(max_length=200, blank=True)
    marked_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='attendance_marked'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'student__last_name']
        unique_together = ['classroom', 'student', 'date']

    def __str__(self):
        return (
            f"{self.student.get_full_name()} — "
            f"{self.date} — {self.get_status_display()}"
        )

    @property
    def status_badge(self):
        colors = {
            'present': 'success',
            'absent': 'danger',
            'late': 'warning',
            'excused': 'info',
        }
        return colors.get(self.status, 'secondary')