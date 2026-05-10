from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.teachers.models import Teacher
from apps.students.models import Grade, Stream, AcademicYear


class Subject(models.Model):
    """A subject taught in the school e.g. Mathematics, English, Biology"""

    class SubjectType(models.TextChoices):
        COMPULSORY = 'compulsory', _('Compulsory')
        ELECTIVE = 'elective', _('Elective')

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    subject_type = models.CharField(
        max_length=20,
        choices=SubjectType.choices,
        default=SubjectType.COMPULSORY
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class ClassRoom(models.Model):
    """
    A specific class — the combination of grade + stream + academic year.
    This is the actual teaching unit. e.g. Grade 7A — 2025/2026
    """
    name = models.CharField(max_length=100)
    grade = models.ForeignKey(
        Grade, on_delete=models.PROTECT, related_name='classrooms'
    )
    stream = models.ForeignKey(
        Stream, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='classrooms'
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name='classrooms'
    )
    class_teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='class_teacher_of'
    )
    capacity = models.PositiveIntegerField(default=40)
    room_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['grade__order', 'stream__name']
        unique_together = ['grade', 'stream', 'academic_year']

    def __str__(self):
        stream_part = f" {self.stream.name}" if self.stream else ""
        return f"{self.grade.name}{stream_part} — {self.academic_year}"

    @property
    def student_count(self):
        return self.grade.students.filter(
            stream=self.stream,
            academic_year=self.academic_year,
            status='active'
        ).count()


class SubjectAssignment(models.Model):
    """
    Links a subject to a classroom and assigns a teacher to teach it.
    e.g. Mr. Kennedy teaches Mathematics in Grade 7A — 2025/2026
    """
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE,
        related_name='subject_assignments'
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT,
        related_name='assignments'
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='subject_assignments'
    )
    periods_per_week = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subject__name']
        unique_together = ['classroom', 'subject']

    def __str__(self):
        return (
            f"{self.subject.name} — {self.classroom} "
            f"({self.teacher.get_full_name() if self.teacher else 'Unassigned'})"
        )


class Term(models.Model):
    """A school term within an academic year"""

    class TermNumber(models.TextChoices):
        TERM_1 = 'term_1', _('Term 1')
        TERM_2 = 'term_2', _('Term 2')
        TERM_3 = 'term_3', _('Term 3')
        SEMESTER_1 = 'semester_1', _('Semester 1')
        SEMESTER_2 = 'semester_2', _('Semester 2')

    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE,
        related_name='terms'
    )
    term = models.CharField(max_length=20, choices=TermNumber.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_date']
        unique_together = ['academic_year', 'term']

    def __str__(self):
        return f"{self.get_term_display()} — {self.academic_year}"

    def save(self, *args, **kwargs):
        if self.is_current:
            Term.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

class AssessmentType(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, default=100,
        help_text='Percentage weight of this assessment'
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.weight}%)"


class GradeEntry(models.Model):
    """
    A single mark entered for one student,
    one subject, one assessment type, one term.
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='grade_entries'
    )
    subject_assignment = models.ForeignKey(
        SubjectAssignment,
        on_delete=models.CASCADE,
        related_name='grade_entries'
    )
    assessment_type = models.ForeignKey(
        AssessmentType,
        on_delete=models.PROTECT,
        related_name='grade_entries'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name='grade_entries'
    )
    marks = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text='Marks scored'
    )
    max_marks = models.DecimalField(
        max_digits=6, decimal_places=2, default=100,
        help_text='Maximum possible marks'
    )
    remarks = models.CharField(max_length=200, blank=True)
    entered_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student__last_name', 'assessment_type__order']
        unique_together = [
            'student', 'subject_assignment',
            'assessment_type', 'term'
        ]

    def __str__(self):
        return (
            f"{self.student.get_full_name()} — "
            f"{self.subject_assignment.subject.name} — "
            f"{self.assessment_type.name}: {self.marks}/{self.max_marks}"
        )

    @property
    def percentage(self):
        if self.max_marks > 0:
            return round(float(self.marks) / float(self.max_marks) * 100, 1)
        return 0

    @property
    def letter_grade(self):
        pct = self.percentage
        if pct >= 80: return 'A'
        elif pct >= 70: return 'B'
        elif pct >= 60: return 'C'
        elif pct >= 50: return 'D'
        else: return 'F'

    @property
    def grade_badge(self):
        grade = self.letter_grade
        colors = {
            'A': 'success', 'B': 'primary',
            'C': 'info', 'D': 'warning', 'F': 'danger'
        }
        return colors.get(grade, 'secondary')