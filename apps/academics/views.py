from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import Subject, ClassRoom, SubjectAssignment, Term, AssessmentType, GradeEntry
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

    from .models import (
    Subject, ClassRoom, SubjectAssignment,
    Term, AssessmentType, GradeEntry
)
from apps.students.models import Student


@method_decorator(login_required, name='dispatch')
class AssessmentTypeListView(ListView):
    model = AssessmentType
    template_name = 'academics/assessment_types.html'
    context_object_name = 'assessment_types'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Assessment Types'
        return ctx


@method_decorator(login_required, name='dispatch')
class AssessmentTypeCreateView(CreateView):
    model = AssessmentType
    fields = ['name', 'short_name', 'weight', 'order', 'is_active']
    template_name = 'academics/assessment_type_form.html'
    success_url = reverse_lazy('academics:assessment_types')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Add Assessment Type'
        for name, field in self.get_form().fields.items():
            widget = field.widget
            if isinstance(widget, get_object_or_404.__class__):
                pass
            widget.attrs['class'] = (
                'form-select kenda-input'
                if hasattr(widget, 'choices')
                else 'form-control kenda-input'
            )
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Assessment type added!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class GradeBookView(ListView):
    model = SubjectAssignment
    template_name = 'academics/gradebook.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        return SubjectAssignment.objects.select_related(
            'classroom__grade', 'classroom__stream',
            'classroom__academic_year', 'subject', 'teacher'
        ).order_by(
            'classroom__grade__order', 'subject__name'
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Grade Book'
        ctx['terms'] = Term.objects.all()
        return ctx


@method_decorator(login_required, name='dispatch')
class GradeBookDetailView(View):
    template_name = 'academics/gradebook_detail.html'

    def get(self, request, assignment_pk):
        assignment = get_object_or_404(
            SubjectAssignment.objects.select_related(
                'classroom__grade', 'classroom__stream',
                'classroom__academic_year', 'subject', 'teacher'
            ),
            pk=assignment_pk
        )
        selected_term_id = request.GET.get('term')
        terms = Term.objects.all()
        selected_term = None

        if selected_term_id:
            selected_term = get_object_or_404(Term, pk=selected_term_id)
        else:
            selected_term = Term.objects.filter(is_current=True).first()

        students = Student.objects.filter(
            grade=assignment.classroom.grade,
            stream=assignment.classroom.stream,
            academic_year=assignment.classroom.academic_year,
            status='active'
        ).order_by('last_name', 'first_name')

        assessment_types = AssessmentType.objects.filter(is_active=True)

        # Build grade matrix
        grade_matrix = {}
        if selected_term:
            entries = GradeEntry.objects.filter(
                subject_assignment=assignment,
                term=selected_term
            ).select_related('student', 'assessment_type')

            for entry in entries:
                if entry.student_id not in grade_matrix:
                    grade_matrix[entry.student_id] = {}
                grade_matrix[entry.student_id][entry.assessment_type_id] = entry

        return render(request, self.template_name, {
            'assignment': assignment,
            'students': students,
            'assessment_types': assessment_types,
            'terms': terms,
            'selected_term': selected_term,
            'grade_matrix': grade_matrix,
            'page_title': (
                f"{assignment.subject.name} — "
                f"{assignment.classroom}"
            ),
        })


@method_decorator(login_required, name='dispatch')
class EnterMarksView(View):
    def post(self, request, assignment_pk):
        assignment = get_object_or_404(SubjectAssignment, pk=assignment_pk)
        term_id = request.POST.get('term')
        term = get_object_or_404(Term, pk=term_id) if term_id else None

        if not term:
            messages.error(request, 'Please select a term.')
            return redirect(
                'academics:gradebook_detail', assignment_pk=assignment_pk
            )

        students = Student.objects.filter(
            grade=assignment.classroom.grade,
            stream=assignment.classroom.stream,
            academic_year=assignment.classroom.academic_year,
            status='active'
        )
        assessment_types = AssessmentType.objects.filter(is_active=True)
        saved = 0

        for student in students:
            for at in assessment_types:
                key = f"marks_{student.pk}_{at.pk}"
                max_key = f"max_{student.pk}_{at.pk}"
                marks_val = request.POST.get(key, '').strip()
                max_val = request.POST.get(max_key, '100').strip()

                if marks_val == '':
                    continue

                try:
                    marks = float(marks_val)
                    max_marks = float(max_val) if max_val else 100
                    GradeEntry.objects.update_or_create(
                        student=student,
                        subject_assignment=assignment,
                        assessment_type=at,
                        term=term,
                        defaults={
                            'marks': marks,
                            'max_marks': max_marks,
                            'entered_by': request.user,
                        }
                    )
                    saved += 1
                except (ValueError, TypeError):
                    pass

        messages.success(request, f'{saved} mark(s) saved successfully!')
        return redirect(
            f"{reverse_lazy('academics:gradebook_detail', kwargs={'assignment_pk': assignment_pk})}?term={term_id}"
        )


@method_decorator(login_required, name='dispatch')
class StudentGradesView(View):
    template_name = 'academics/student_grades.html'

    def get(self, request, student_pk):
        student = get_object_or_404(Student, pk=student_pk)
        terms = Term.objects.all()
        selected_term_id = request.GET.get('term')
        selected_term = None

        if selected_term_id:
            selected_term = get_object_or_404(Term, pk=selected_term_id)
        else:
            selected_term = Term.objects.filter(is_current=True).first()

        entries = GradeEntry.objects.filter(
            student=student
        ).select_related(
            'subject_assignment__subject',
            'assessment_type', 'term'
        ).order_by(
            'subject_assignment__subject__name',
            'assessment_type__order'
        )

        if selected_term:
            entries = entries.filter(term=selected_term)

        # Group by subject
        subjects_data = {}
        for entry in entries:
            subj = entry.subject_assignment.subject.name
            if subj not in subjects_data:
                subjects_data[subj] = []
            subjects_data[subj].append(entry)

        return render(request, self.template_name, {
            'student': student,
            'subjects_data': subjects_data,
            'terms': terms,
            'selected_term': selected_term,
            'page_title': f"Grades — {student.get_full_name()}",
        })    