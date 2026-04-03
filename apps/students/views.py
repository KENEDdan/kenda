import csv
import io
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView, DetailView, CreateView,
    UpdateView, DeleteView, View, TemplateView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from .models import Student, Grade, Stream, AcademicYear
from .forms import StudentEnrolForm, StudentImportForm


@method_decorator(login_required, name='dispatch')
class StudentListView(ListView):
    model = Student
    template_name = 'students/list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        qs = Student.objects.select_related('grade', 'stream', 'academic_year')
        q = self.request.GET.get('q')
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(student_id__icontains=q) |
                Q(guardian_name__icontains=q)
            )
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        grade = self.request.GET.get('grade')
        if grade:
            qs = qs.filter(grade_id=grade)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'All Students'
        ctx['total'] = Student.objects.count()
        ctx['active'] = Student.objects.filter(status='active').count()
        ctx['grades'] = Grade.objects.all()
        ctx['status_choices'] = Student.Status.choices
        return ctx


@method_decorator(login_required, name='dispatch')
class StudentEnrolView(CreateView):
    model = Student
    form_class = StudentEnrolForm
    template_name = 'students/enrol.html'
    success_url = reverse_lazy('students:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Enrol Student'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Student enrolled successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
class StudentDetailView(DetailView):
    model = Student
    template_name = 'students/detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.object.get_full_name()
        ctx['status_choices'] = Student.Status.choices
        return ctx


@method_decorator(login_required, name='dispatch')
class StudentEditView(UpdateView):
    model = Student
    form_class = StudentEnrolForm
    template_name = 'students/enrol.html'
    context_object_name = 'student'

    def get_success_url(self):
        return reverse_lazy('students:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Edit — {self.object.get_full_name()}"
        ctx['is_edit'] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Student record updated.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'students/confirm_delete.html'
    success_url = reverse_lazy('students:list')
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Delete Student'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'Student {self.object.get_full_name()} has been deleted.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class StudentStatusChangeView(View):
    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(Student.Status.choices):
            old_status = student.get_status_display()
            student.status = new_status
            student.save()
            messages.success(
                request,
                f"{student.get_full_name()}'s status changed from "
                f"{old_status} to {student.get_status_display()}."
            )
        else:
            messages.error(request, 'Invalid status.')
        return redirect('students:detail', pk=pk)


@method_decorator(login_required, name='dispatch')
class StudentIDCardView(DetailView):
    model = Student
    template_name = 'students/id_card.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"ID Card — {self.object.get_full_name()}"
        return ctx


@method_decorator(login_required, name='dispatch')
class StudentImportView(View):
    template_name = 'students/import.html'

    def get(self, request):
        form = StudentImportForm()
        return self._render(request, form)

    def post(self, request):
        form = StudentImportForm(request.POST, request.FILES)
        if not form.is_valid():
            return self._render(request, form)

        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid .csv file.')
            return self._render(request, form)

        decoded = csv_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))

        success_count = 0
        error_rows = []

        for i, row in enumerate(reader, start=2):
            try:
                grade = Grade.objects.get(name__iexact=row.get('grade', '').strip())
                academic_year = AcademicYear.objects.get(is_current=True)
                Student.objects.create(
                    first_name=row['first_name'].strip(),
                    last_name=row['last_name'].strip(),
                    middle_name=row.get('middle_name', '').strip(),
                    gender=row.get('gender', 'male').strip().lower(),
                    date_of_birth=row['date_of_birth'].strip(),
                    grade=grade,
                    academic_year=academic_year,
                    guardian_name=row['guardian_name'].strip(),
                    guardian_phone=row['guardian_phone'].strip(),
                    phone=row.get('phone', '').strip(),
                    email=row.get('email', '').strip(),
                    nationality=row.get('nationality', '').strip(),
                )
                success_count += 1
            except Exception as e:
                error_rows.append(f"Row {i}: {str(e)}")

        if success_count:
            messages.success(request, f'{success_count} student(s) imported successfully!')
        if error_rows:
            messages.warning(request, f'{len(error_rows)} row(s) failed. Check details below.')

        return self._render(request, form, error_rows)

    def _render(self, request, form, error_rows=None):
        from django.shortcuts import render
        return render(request, self.template_name, {
            'form': form,
            'page_title': 'Import Students',
            'error_rows': error_rows or [],
        })