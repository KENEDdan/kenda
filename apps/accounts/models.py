import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Kenda custom user model.
    Uses email as the login field and UUID as the primary key.
    Roles control which dashboard the user sees after login.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", _("Administrator")
        TEACHER = "teacher", _("Teacher / Lecturer")
        STUDENT = "student", _("Student")
        PARENT = "parent", _("Parent / Guardian")
        STAFF = "staff", _("Staff")

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False,
    )
    email = models.EmailField(
        unique=True, verbose_name=_("Email Address"),
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_("Role"),
    )
    phone_number = models.CharField(
        max_length=20, blank=True, verbose_name=_("Phone"),
    )
    profile_photo = models.ImageField(
        upload_to="profiles/%Y/%m/", null=True, blank=True,
    )
    two_fa_enabled = models.BooleanField(
        default=False, verbose_name=_("2FA Enabled"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    @property
    def is_admin(self): return self.role == self.Role.ADMIN

    @property
    def is_teacher(self): return self.role == self.Role.TEACHER

    @property
    def is_student(self): return self.role == self.Role.STUDENT

    @property
    def is_parent(self): return self.role == self.Role.PARENT