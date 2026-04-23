from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView, DeleteView, View
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum, Count, Q

from .models import FeeCategory, FeeStructure, Invoice, InvoiceItem, Payment
from .forms import (
    FeeCategoryForm, FeeStructureForm,
    InvoiceCreateForm, PaymentForm
)
from apps.students.models import Student, Grade, AcademicYear


@method_decorator(login_required, name='dispatch')
class FeeDashboardView(TemplateView):
    template_name = 'fees/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Fee Management'

        # Summary stats
        ctx['total_invoiced'] = Invoice.objects.aggregate(
            t=Sum('total_amount')
        )['t'] or 0
        ctx['total_collected'] = Invoice.objects.aggregate(
            t=Sum('amount_paid')
        )['t'] or 0
        ctx['total_outstanding'] = ctx['total_invoiced'] - ctx['total_collected']

        ctx['invoices_count'] = Invoice.objects.count()
        ctx['unpaid_count'] = Invoice.objects.filter(
            status__in=['unpaid', 'overdue']
        ).count()
        ctx['paid_count'] = Invoice.objects.filter(status='paid').count()

        # Recent invoices
        ctx['recent_invoices'] = Invoice.objects.select_related(
            'student', 'academic_year', 'term'
        ).order_by('-created_at')[:10]

        # Arrears — students with outstanding balance
        ctx['arrears'] = Invoice.objects.filter(
            status__in=['unpaid', 'partial', 'overdue']
        ).select_related('student').order_by('-total_amount')[:10]

        return ctx


@method_decorator(login_required, name='dispatch')
class FeeCategoryListView(ListView):
    model = FeeCategory
    template_name = 'fees/categories.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Fee Categories'
        return ctx


@method_decorator(login_required, name='dispatch')
class FeeCategoryCreateView(CreateView):
    model = FeeCategory
    form_class = FeeCategoryForm
    template_name = 'fees/category_form.html'
    success_url = reverse_lazy('fees:categories')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Add Fee Category'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Fee category added!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class FeeCategoryEditView(UpdateView):
    model = FeeCategory
    form_class = FeeCategoryForm
    template_name = 'fees/category_form.html'
    success_url = reverse_lazy('fees:categories')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Edit — {self.object.name}"
        ctx['is_edit'] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Category updated.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class FeeStructureListView(ListView):
    model = FeeStructure
    template_name = 'fees/structures.html'
    context_object_name = 'structures'

    def get_queryset(self):
        return FeeStructure.objects.select_related(
            'category', 'grade', 'academic_year', 'term'
        ).order_by('grade__order', 'category__name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Fee Structures'
        return ctx


@method_decorator(login_required, name='dispatch')
class FeeStructureCreateView(CreateView):
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'fees/structure_form.html'
    success_url = reverse_lazy('fees:structures')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Add Fee Structure'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Fee structure added!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class FeeStructureEditView(UpdateView):
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'fees/structure_form.html'
    success_url = reverse_lazy('fees:structures')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Edit Fee Structure'
        ctx['is_edit'] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Fee structure updated.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class FeeStructureDeleteView(DeleteView):
    model = FeeStructure
    template_name = 'fees/structure_confirm_delete.html'
    success_url = reverse_lazy('fees:structures')
    context_object_name = 'structure'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Delete Fee Structure'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Fee structure deleted.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class InvoiceListView(ListView):
    model = Invoice
    template_name = 'fees/invoices.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        qs = Invoice.objects.select_related(
            'student', 'academic_year', 'term'
        )
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(invoice_number__icontains=q) |
                Q(student__first_name__icontains=q) |
                Q(student__last_name__icontains=q) |
                Q(student__student_id__icontains=q)
            )
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Invoices'
        ctx['status_choices'] = Invoice.Status.choices
        return ctx


@method_decorator(login_required, name='dispatch')
class InvoiceCreateView(View):
    template_name = 'fees/invoice_create.html'

    def get(self, request):
        form = InvoiceCreateForm()
        return render(request, self.template_name, {
            'form': form,
            'page_title': 'Create Invoice',
        })

    def post(self, request):
        form = InvoiceCreateForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                'form': form,
                'page_title': 'Create Invoice',
            })

        student = form.cleaned_data['student']
        academic_year = form.cleaned_data['academic_year']
        term = form.cleaned_data.get('term')
        due_date = form.cleaned_data.get('due_date')
        notes = form.cleaned_data.get('notes', '')

        # Get fee structures for this student's grade
        structures = FeeStructure.objects.filter(
            grade=student.grade,
            academic_year=academic_year,
            is_active=True
        )
        if term:
            structures = structures.filter(
                Q(term=term) | Q(term__isnull=True)
            )

        if not structures.exists():
            messages.warning(
                request,
                'No fee structures found for this student\'s grade. '
                'Please set up fee structures first.'
            )
            return render(request, self.template_name, {
                'form': form,
                'page_title': 'Create Invoice',
            })

        total = sum(s.amount for s in structures)

        invoice = Invoice.objects.create(
            student=student,
            academic_year=academic_year,
            term=term,
            total_amount=total,
            due_date=due_date,
            notes=notes,
        )

        for structure in structures:
            InvoiceItem.objects.create(
                invoice=invoice,
                category=structure.category,
                description=structure.category.name,
                amount=structure.amount,
            )

        messages.success(
            request,
            f'Invoice {invoice.invoice_number} created for '
            f'{student.get_full_name()} — Total: {total}'
        )
        return redirect('fees:invoice_detail', pk=invoice.pk)


@method_decorator(login_required, name='dispatch')
class InvoiceDetailView(View):
    template_name = 'fees/invoice_detail.html'

    def get(self, request, pk):
        invoice = get_object_or_404(
            Invoice.objects.select_related(
                'student', 'academic_year', 'term'
            ).prefetch_related('items__category', 'payments'),
            pk=pk
        )
        payment_form = PaymentForm()
        return render(request, self.template_name, {
            'invoice': invoice,
            'payment_form': payment_form,
            'page_title': invoice.invoice_number,
        })


@method_decorator(login_required, name='dispatch')
class RecordPaymentView(View):
    def post(self, request, invoice_pk):
        invoice = get_object_or_404(Invoice, pk=invoice_pk)
        form = PaymentForm(request.POST)

        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.recorded_by = request.user
            payment.save()
            messages.success(
                request,
                f'Payment of {payment.amount} recorded. '
                f'Receipt: {payment.receipt_number}'
            )
        else:
            messages.error(request, 'Please fix the payment form errors.')

        return redirect('fees:invoice_detail', pk=invoice_pk)


@method_decorator(login_required, name='dispatch')
class StudentFeesView(View):
    template_name = 'fees/student_fees.html'

    def get(self, request, student_pk):
        student = get_object_or_404(Student, pk=student_pk)
        invoices = Invoice.objects.filter(
            student=student
        ).select_related('academic_year', 'term').prefetch_related(
            'items', 'payments'
        ).order_by('-created_at')

        total_invoiced = sum(i.total_amount for i in invoices)
        total_paid = sum(i.amount_paid for i in invoices)
        total_balance = total_invoiced - total_paid

        return render(request, self.template_name, {
            'student': student,
            'invoices': invoices,
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'total_balance': total_balance,
            'page_title': f"Fees — {student.get_full_name()}",
        })