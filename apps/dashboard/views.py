from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.shortcuts import redirect


class LoginRequiredMixin:
    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return login_required(view)


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/admin.html"

    def get(self, request, *args, **kwargs):
        from apps.school.models import SchoolProfile
        school = SchoolProfile.objects.filter(pk=1).first()
        # If school name is still default or not set up, redirect to settings
        if not school or school.name == 'My School':
            from django.contrib import messages
            messages.info(
                request,
                'Welcome to Kenda! Please complete your school profile to get started.'
            )
            return redirect('school:settings')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.students.models import Student
        from apps.teachers.models import Teacher
        ctx['page_title'] = 'Admin Dashboard'
        ctx['stats'] = [
            {
                'label': 'Total Students',
                'value': Student.objects.count(),
                'icon': 'bi-people-fill',
                'color': 'kenda-stat-purple',
            },
            {
                'label': 'Total Teachers',
                'value': Teacher.objects.count(),
                'icon': 'bi-person-workspace',
                'color': 'kenda-stat-blue',
            },
            {
                'label': 'Fees Collected',
                'value': '$0',
                'icon': 'bi-cash-stack',
                'color': 'kenda-stat-gold',
            },
            {
                'label': 'Active Students',
                'value': Student.objects.filter(status='active').count(),
                'icon': 'bi-journal-check',
                'color': 'kenda-stat-green',
            },
        ]
        ctx['recent_students'] = Student.objects.select_related(
            'grade', 'stream'
        ).order_by('-created_at')[:5]
        return ctx


class TeacherDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/teacher.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Teacher Dashboard'
        return ctx


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/student.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Student Dashboard'
        return ctx


class ParentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/parent.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Parent Dashboard'
        return ctx


class StaffDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/staff.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Staff Dashboard'
        return ctx