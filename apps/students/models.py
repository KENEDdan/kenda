import uuid
import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import CustomUser


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Grade(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Stream(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='streams')
    name = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField(default=40)

    class Meta:
        unique_together = ['grade', 'name']

    def __str__(self):
        return f"{self.grade.name} {self.name}"

    @property
    def current_enrollment(self):
        return self.students.filter(status='active').count()

    @property
    def is_full(self):
        return self.current_enrollment >= self.capacity


class Student(models.Model):

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')
        GRADUATED = 'graduated', _('Graduated')
        SUSPENDED = 'suspended', _('Suspended')
        TRANSFERRED = 'transferred', _('Transferred')

    class Gender(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='student_profile'
    )
    student_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    date_of_birth = models.DateField()
    photo = models.ImageField(upload_to='students/photos/%Y/', null=True, blank=True)

    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, related_name='students')
    stream = models.ForeignKey(
        Stream, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students'
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name='students'
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    enrollment_date = models.DateField(auto_now_add=True)

    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    nationality = models.CharField(max_length=100, blank=True)

    guardian_name = models.CharField(max_length=200)
    guardian_phone = models.CharField(max_length=20)
    guardian_email = models.EmailField(blank=True)
    guardian_relationship = models.CharField(max_length=50, default='Parent')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.student_id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = self._generate_student_id()
        super().save(*args, **kwargs)

    def _generate_student_id(self):
        year = datetime.date.today().year
        count = Student.objects.filter(created_at__year=year).count() + 1
        return f"KND{year}{count:04d}"

    @property
    def status_badge(self):
        colors = {
            'active': 'success',
            'inactive': 'secondary',
            'graduated': 'info',
            'suspended': 'danger',
            'transferred': 'warning',
        }
        return colors.get(self.status, 'secondary')


class StudentPromotion(models.Model):
    """Records each time a student is promoted or held back."""

    class Result(models.TextChoices):
        PROMOTED = 'promoted', _('Promoted')
        REPEATED = 'repeated', _('Repeated Year')
        GRADUATED = 'graduated', _('Graduated')

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='promotions'
    )
    from_grade = models.ForeignKey(
        Grade, on_delete=models.PROTECT, related_name='promotions_from'
    )
    to_grade = models.ForeignKey(
        Grade, on_delete=models.PROTECT,
        related_name='promotions_to', null=True, blank=True
    )
    from_academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name='promotions_from'
    )
    to_academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT,
        related_name='promotions_to', null=True, blank=True
    )
    result = models.CharField(
        max_length=20, choices=Result.choices, default=Result.PROMOTED
    )
    notes = models.TextField(blank=True)
    promoted_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    promoted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-promoted_at']

    def __str__(self):
        return (
            f"{self.student.get_full_name()} — "
            f"{self.from_grade} → {self.to_grade or 'Graduated'}"
        )