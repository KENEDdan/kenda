import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import CustomUser


class AcademicYear(models.Model):
    """e.g. 2024/2025"""
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
        # Only one academic year can be current at a time
        if self.is_current:
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Grade(models.Model):
    """A grade/class level e.g. Grade 1, Form 3, Year 2"""
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Stream(models.Model):
    """A section within a grade e.g. Grade 1A, Grade 1B"""
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
    """Core student record."""

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

    # Identity
    student_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    date_of_birth = models.DateField()
    photo = models.ImageField(upload_to='students/photos/%Y/', null=True, blank=True)

    # Academic placement
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, related_name='students')
    stream = models.ForeignKey(
        Stream, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students'
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name='students'
    )

    # Enrollment
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    enrollment_date = models.DateField(auto_now_add=True)

    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    nationality = models.CharField(max_length=100, blank=True)

    # Guardian
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
        import datetime
        year = datetime.date.today().year
        count = Student.objects.filter(
            created_at__year=year
        ).count() + 1
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