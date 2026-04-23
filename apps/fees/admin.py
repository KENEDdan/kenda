from django.contrib import admin
from .models import FeeCategory, FeeStructure, Invoice, InvoiceItem, Payment


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('category', 'grade', 'academic_year', 'amount', 'is_active')
    list_filter = ('academic_year', 'grade', 'is_active')


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('receipt_number', 'created_at')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number', 'student', 'total_amount',
        'amount_paid', 'balance', 'status'
    )
    list_filter = ('status', 'academic_year', 'term')
    search_fields = (
        'invoice_number', 'student__first_name',
        'student__last_name', 'student__student_id'
    )
    readonly_fields = ('invoice_number', 'created_at', 'updated_at')
    inlines = [InvoiceItemInline, PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_number', 'invoice', 'amount',
        'payment_method', 'payment_date'
    )
    list_filter = ('payment_method', 'payment_date')
    readonly_fields = ('receipt_number', 'created_at')