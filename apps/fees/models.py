from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.students.models import Student, Grade, AcademicYear
from apps.academics.models import Term


class FeeCategory(models.Model):
    """Types of fees e.g. Tuition, Boarding, Transport, Activity"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Fee Categories'

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    """
    Defines how much a specific grade pays for a specific
    fee category in a specific term.
    """
    category = models.ForeignKey(
        FeeCategory, on_delete=models.PROTECT,
        related_name='structures'
    )
    grade = models.ForeignKey(
        Grade, on_delete=models.PROTECT,
        related_name='fee_structures'
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT,
        related_name='fee_structures'
    )
    term = models.ForeignKey(
        Term, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='fee_structures'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['grade__order', 'category__name']

    def __str__(self):
        return (
            f"{self.category.name} — {self.grade.name} — "
            f"{self.academic_year} ({self.amount})"
        )


class Invoice(models.Model):
    """A fee invoice issued to a student for a term."""

    class Status(models.TextChoices):
        UNPAID = 'unpaid', _('Unpaid')
        PARTIAL = 'partial', _('Partially Paid')
        PAID = 'paid', _('Fully Paid')
        WAIVED = 'waived', _('Waived')
        OVERDUE = 'overdue', _('Overdue')

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name='invoices'
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT,
        related_name='invoices'
    )
    term = models.ForeignKey(
        Term, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='invoices'
    )
    invoice_number = models.CharField(
        max_length=30, unique=True, editable=False
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.UNPAID
    )
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} — {self.student.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self._generate_invoice_number()
        self._update_status()
        super().save(*args, **kwargs)

    def _generate_invoice_number(self):
        import datetime
        year = datetime.date.today().year
        count = Invoice.objects.filter(
            created_at__year=year
        ).count() + 1
        return f"INV{year}{count:05d}"

    def _update_status(self):
        import datetime
        if self.amount_paid >= self.total_amount:
            self.status = self.Status.PAID
        elif self.amount_paid > 0:
            self.status = self.Status.PARTIAL
        elif (self.due_date and
              self.due_date < datetime.date.today() and
              self.amount_paid == 0):
            self.status = self.Status.OVERDUE
        else:
            self.status = self.Status.UNPAID

    @property
    def balance(self):
        return self.total_amount - self.amount_paid

    @property
    def status_badge(self):
        colors = {
            'unpaid': 'danger',
            'partial': 'warning',
            'paid': 'success',
            'waived': 'info',
            'overdue': 'danger',
        }
        return colors.get(self.status, 'secondary')


class InvoiceItem(models.Model):
    """A line item on an invoice."""
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE,
        related_name='items'
    )
    category = models.ForeignKey(
        FeeCategory, on_delete=models.PROTECT
    )
    description = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.category.name} — {self.amount}"


class Payment(models.Model):
    """A payment made against an invoice."""

    class Method(models.TextChoices):
        CASH = 'cash', _('Cash')
        MOBILE_MONEY = 'mobile_money', _('Mobile Money')
        BANK_TRANSFER = 'bank_transfer', _('Bank Transfer')
        CHEQUE = 'cheque', _('Cheque')
        OTHER = 'other', _('Other')

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=20, choices=Method.choices,
        default=Method.CASH
    )
    payment_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    receipt_number = models.CharField(
        max_length=30, unique=True, editable=False
    )
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.receipt_number} — {self.amount}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self._generate_receipt()
        super().save(*args, **kwargs)
        # Update invoice amount paid
        total_paid = sum(
            p.amount for p in self.invoice.payments.all()
        )
        self.invoice.amount_paid = total_paid
        self.invoice._update_status()
        Invoice.objects.filter(pk=self.invoice.pk).update(
            amount_paid=total_paid,
            status=self.invoice.status
        )

    def _generate_receipt(self):
        import datetime
        year = datetime.date.today().year
        count = Payment.objects.filter(
            created_at__year=year
        ).count() + 1
        return f"RCP{year}{count:05d}"