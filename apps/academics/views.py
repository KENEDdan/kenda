from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import Subject, ClassRoom, SubjectAssignment, Term
from .forms import SubjectForm, ClassRoomForm, SubjectAssignmentForm, TermForm


# ── Subject Views ─────────────────────────────────────────────────────────────

@method_decorator(login_required, name='dispatch')
class SubjectListView(ListView):
    model = Subject
    template_name = 'academics/subject_list.html'
    context_object_name = 'subjects'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Subjects'
        ctx['total'] = Subject.objects.count()
        ctx['active'] = Subject.objects.filter(is_active=True).count()
        return ctx


@method_decorator(login_required, name='dispatch')
class SubjectCreateView(CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'academics/subject_form.html'
    success_url = reverse_lazy('academics:subject_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Add Subject'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Subject added successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class SubjectEditView(UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'academics/subject_form.html'
    success_url = reverse_lazy('academics:subject_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Edit — {self.object.name}"
        ctx['is_edit'] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Subject updated.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = 'academics/subject_confirm_delete.html'
    success_url = reverse_lazy('academics:subject_list')
    context_object_name = 'subject'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Delete Subject'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'Subject {self.object.name} deleted.')
        return super().form_valid(form)


# ── ClassRoom Views ───────────────────────────────────────────────────────────

@method_decorator(login_required, name='dispatch')
class ClassRoomListView(ListView):
    model = ClassRoom
    template_name = 'academics/class_list.html'
    context_object_name = 'classrooms'

    def get_queryset(self):
        return ClassRoom.objects.select_related(
            'grade', 'stream', 'academic_year', 'class_teacher'
        ).order_by('grade__order', 'stream__name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Classes'
        ctx['total'] = ClassRoom.objects.count()
        ctx['active'] = ClassRoom.objects.filter(is_active=True).count()
        return ctx


@method_decorator(login_required, name='dispatch')
class ClassRoomCreateView(CreateView):
    model = ClassRoom
    form_class = ClassRoomForm
    template_name = 'academics/class_form.html'
    success_url = reverse_lazy('academics:class_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Create Class'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Class created successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please fix the errors below.')
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
class ClassRoomDetailView(DetailView):
    model = ClassRoom
    template_name = 'academics/class_detail.html'
    context_object_name = 'classroom'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = str(self.object)
        ctx['assignments'] = self.object.subject_assignments.select_related(
            'subject', 'teacher'
        )
        ctx['assign_form'] = SubjectAssignmentForm()
        # Students in this class
        ctx['students'] = self.object.grade.students.filter(
            stream=self.object.stream,
            academic_year=self.object.academic_year,
            status='active'
        ).order_by('last_name', 'first_name')
        return ctx


@method_decorator(login_required, name='dispatch')
class ClassRoomEditView(UpdateView):
    model = ClassRoom
    form_class = ClassRoomForm
    template_name = 'academics/class_form.html'
    context_object_name = 'classroom'

    def get_success_url(self):
        return reverse_lazy('academics:class_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Edit — {self.object}"
        ctx['is_edit'] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Class updated.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ClassRoomDeleteView(DeleteView):
    model = ClassRoom
    template_name = 'academics/class_confirm_delete.html'
    success_url = reverse_lazy('academics:class_list')
    context_object_name = 'classroom'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Delete Class'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'Class {self.object} deleted.')
        return super().form_valid(form)


# ── Subject Assignment Views ──────────────────────────────────────────────────

@method_decorator(login_required, name='dispatch')
class SubjectAssignView(View):
    def post(self, request, pk):
        classroom = get_object_or_404(ClassRoom, pk=pk)
        form = SubjectAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.classroom = classroom
            try:
                assignment.save()
                messages.success(
                    request,
                    f'{assignment.subject.name} assigned successfully!'
                )
            except Exception:
                messages.error(
                    request,
                    'This subject is already assigned to this class.'
                )
        else:
            messages.error(request, 'Please fix the errors.')
        return redirect('academics:class_detail', pk=pk)


@method_decorator(login_required, name='dispatch')
class SubjectAssignDeleteView(View):
    def post(self, request, pk):
        assignment = get_object_or_404(SubjectAssignment, pk=pk)
        classroom_pk = assignment.classroom.pk
        subject_name = assignment.subject.name
        assignment.delete()
        messages.success(request, f'{subject_name} removed from class.')
        return redirect('academics:class_detail', pk=classroom_pk)


# ── Term Views ────────────────────────────────────────────────────────────────

@method_decorator(login_required, name='dispatch')
class TermListView(ListView):
    model = Term
    template_name = 'academics/term_list.html'
    context_object_name = 'terms'

    def get_queryset(self):
        return Term.objects.select_related('academic_year').order_by(
            '-academic_year__start_date', 'start_date'
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Terms & Semesters'
        return ctx


@method_decorator(login_required, name='dispatch')
class TermCreateView(CreateView):
    model = Term
    form_class = TermForm
    template_name = 'academics/term_form.html'
    success_url = reverse_lazy('academics:term_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Add Term'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Term added successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class TermEditView(UpdateView):
    model = Term
    form_class = TermForm
    template_name = 'academics/term_form.html'
    success_url = reverse_lazy('academics:term_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Edit — {self.object}"
        ctx['is_edit'] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Term updated.')
        return super().form_valid(form)