from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import CustomUser
from apps.students.models import Grade, AcademicYear


class Announcement(models.Model):

    class Audience(models.TextChoices):
        ALL = 'all', _('Everyone')
        STUDENTS = 'students', _('All Students')
        TEACHERS = 'teachers', _('All Teachers')
        PARENTS = 'parents', _('Parents / Guardians')
        STAFF = 'staff', _('Staff Only')

    class Priority(models.TextChoices):
        NORMAL = 'normal', _('Normal')
        IMPORTANT = 'important', _('Important')
        URGENT = 'urgent', _('Urgent')

    title = models.CharField(max_length=200)
    body = models.TextField()
    audience = models.CharField(
        max_length=20,
        choices=Audience.choices,
        default=Audience.ALL
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL
    )
    grade = models.ForeignKey(
        Grade, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='announcements',
        help_text='Leave blank to target all grades'
    )
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, related_name='announcements'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def priority_badge(self):
        colors = {
            'normal': 'secondary',
            'important': 'warning',
            'urgent': 'danger',
        }
        return colors.get(self.priority, 'secondary')


class Notification(models.Model):
    """In-app notification for a specific user."""

    class Type(models.TextChoices):
        ANNOUNCEMENT = 'announcement', _('Announcement')
        FEE_REMINDER = 'fee_reminder', _('Fee Reminder')
        ATTENDANCE = 'attendance', _('Attendance Alert')
        RESULT = 'result', _('Result Published')
        GENERAL = 'general', _('General')

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.GENERAL
    )
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.user.get_full_name()}"