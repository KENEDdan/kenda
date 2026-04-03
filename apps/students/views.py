from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Student, Grade, Stream, AcademicYear
from .forms import StudentEnrolForm


@method_decorator(login_required, name='dispatch')
class StudentListView(ListView):
    model = Student
    template_name = 'students/list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        qs = Student.objects.select_related('grade', 'stream', 'academic_year')
        # Search
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                first_name__icontains=q
            ) | qs.filter(
                last_name__icontains=q
            ) | qs.filter(
                student_id__icontains=q
            )
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        # Filter by grade
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
        ctx['page_title'] = f"{self.object.get_full_name()}"
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