import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import CustomUser


class Department(models.Model):
    """e.g. Sciences, Humanities, Mathematics"""
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20, blank=True)
    head = models.ForeignKey(
        'Teacher', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='headed_department'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Teacher(models.Model):

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')
        ON_LEAVE = 'on_leave', _('On Leave')
        TERMINATED = 'terminated', _('Terminated')

    class Gender(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')

    class EmploymentType(models.TextChoices):
        FULL_TIME = 'full_time', _('Full Time')
        PART_TIME = 'part_time', _('Part Time')
        CONTRACT = 'contract', _('Contract')
        VOLUNTEER = 'volunteer', _('Volunteer')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='teacher_profile'
    )

    # Identity
    teacher_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(
        upload_to='teachers/photos/%Y/', null=True, blank=True
    )
    nationality = models.CharField(max_length=100, blank=True)

    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    # Employment
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='teachers'
    )
    employment_type = models.CharField(
        max_length=20, choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME
    )
    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.ACTIVE
    )
    join_date = models.DateField(auto_now_add=True)
    qualification = models.CharField(max_length=200, blank=True)
    specialization = models.CharField(max_length=200, blank=True)

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.teacher_id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.teacher_id:
            self.teacher_id = self._generate_teacher_id()
        super().save(*args, **kwargs)

    def _generate_teacher_id(self):
        import datetime
        year = datetime.date.today().year
        count = Teacher.objects.filter(
            created_at__year=year
        ).count() + 1
        return f"TCH{year}{count:04d}"

    @property
    def status_badge(self):
        colors = {
            'active': 'success',
            'inactive': 'secondary',
            'on_leave': 'warning',
            'terminated': 'danger',
        }
        return colors.get(self.status, 'secondary')