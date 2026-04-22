import datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Count, Q

from apps.academics.models import ClassRoom, Term
from apps.students.models import Student
from .models import AttendanceRecord


@method_decorator(login_required, name='dispatch')
class AttendanceDashboardView(TemplateView):
    template_name = 'attendance/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Attendance'
        ctx['classrooms'] = ClassRoom.objects.select_related(
            'grade', 'stream', 'academic_year', 'class_teacher'
        ).filter(is_active=True).order_by('grade__order')
        ctx['today'] = datetime.date.today()

        # Today's marking status per class
        today = datetime.date.today()
        marked_today = AttendanceRecord.objects.filter(
            date=today
        ).values_list('classroom_id', flat=True).distinct()
        ctx['marked_today'] = set(marked_today)

        return ctx


@method_decorator(login_required, name='dispatch')
class MarkAttendanceView(View):
    template_name = 'attendance/mark.html'

    def get(self, request, classroom_pk):
        classroom = get_object_or_404(ClassRoom, pk=classroom_pk)
        date_str = request.GET.get('date', str(datetime.date.today()))
        try:
            selected_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            selected_date = datetime.date.today()

        # Get students in this class
        students = Student.objects.filter(
            grade=classroom.grade,
            stream=classroom.stream,
            academic_year=classroom.academic_year,
            status='active'
        ).order_by('last_name', 'first_name')

        # Get existing attendance for this date
        existing = AttendanceRecord.objects.filter(
            classroom=classroom,
            date=selected_date
        ).select_related('student')

        existing_map = {r.student_id: r for r in existing}
        already_marked = existing.exists()

        return render(request, self.template_name, {
            'classroom': classroom,
            'students': students,
            'selected_date': selected_date,
            'existing_map': existing_map,
            'already_marked': already_marked,
            'status_choices': AttendanceRecord.Status.choices,
            'page_title': f"Attendance — {classroom}",
        })

    def post(self, request, classroom_pk):
        classroom = get_object_or_404(ClassRoom, pk=classroom_pk)
        date_str = request.POST.get('date', str(datetime.date.today()))
        try:
            selected_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            selected_date = datetime.date.today()

        students = Student.objects.filter(
            grade=classroom.grade,
            stream=classroom.stream,
            academic_year=classroom.academic_year,
            status='active'
        )

        current_term = Term.objects.filter(is_current=True).first()
        saved = 0

        for student in students:
            status = request.POST.get(f'status_{student.pk}', 'present')
            notes = request.POST.get(f'notes_{student.pk}', '')

            AttendanceRecord.objects.update_or_create(
                classroom=classroom,
                student=student,
                date=selected_date,
                defaults={
                    'status': status,
                    'notes': notes,
                    'term': current_term,
                    'marked_by': request.user,
                }
            )
            saved += 1

        messages.success(
            request,
            f'Attendance saved for {saved} student(s) on '
            f'{selected_date.strftime("%B %d, %Y")}.'
        )
        return redirect('attendance:dashboard')


@method_decorator(login_required, name='dispatch')
class AttendanceHistoryView(View):
    template_name = 'attendance/history.html'

    def get(self, request, classroom_pk):
        classroom = get_object_or_404(ClassRoom, pk=classroom_pk)

        # Get last 30 days of attendance
        records = AttendanceRecord.objects.filter(
            classroom=classroom
        ).select_related('student').order_by('-date', 'student__last_name')

        # Group by date
        dates = records.values_list('date', flat=True).distinct()[:30]

        return render(request, self.template_name, {
            'classroom': classroom,
            'records': records,
            'dates': dates,
            'page_title': f"Attendance History — {classroom}",
            'status_choices': AttendanceRecord.Status.choices,
        })


@method_decorator(login_required, name='dispatch')
class StudentAttendanceView(View):
    template_name = 'attendance/student.html'

    def get(self, request, student_pk):
        student = get_object_or_404(Student, pk=student_pk)
        records = AttendanceRecord.objects.filter(
            student=student
        ).order_by('-date')

        total = records.count()
        present = records.filter(status='present').count()
        absent = records.filter(status='absent').count()
        late = records.filter(status='late').count()
        excused = records.filter(status='excused').count()

        attendance_pct = round((present / total * 100), 1) if total > 0 else 0

        return render(request, self.template_name, {
            'student': student,
            'records': records[:60],
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'attendance_pct': attendance_pct,
            'page_title': f"Attendance — {student.get_full_name()}",
        })


@method_decorator(login_required, name='dispatch')
class AttendanceReportView(View):
    template_name = 'attendance/report.html'

    def get(self, request):
        classrooms = ClassRoom.objects.filter(
            is_active=True
        ).select_related('grade', 'stream')

        selected_classroom_id = request.GET.get('classroom')
        selected_date_from = request.GET.get('date_from', '')
        selected_date_to = request.GET.get('date_to', '')

        records = None
        summary = None

        if selected_classroom_id:
            classroom = get_object_or_404(
                ClassRoom, pk=selected_classroom_id
            )
            records = AttendanceRecord.objects.filter(
                classroom=classroom
            ).select_related('student')

            if selected_date_from:
                records = records.filter(date__gte=selected_date_from)
            if selected_date_to:
                records = records.filter(date__lte=selected_date_to)

            # Summary per student
            students = Student.objects.filter(
                grade=classroom.grade,
                stream=classroom.stream,
                academic_year=classroom.academic_year,
                status='active'
            )
            summary = []
            for student in students:
                student_records = records.filter(student=student)
                total = student_records.count()
                present = student_records.filter(status='present').count()
                absent = student_records.filter(status='absent').count()
                late = student_records.filter(status='late').count()
                pct = round((present / total * 100), 1) if total > 0 else 0
                summary.append({
                    'student': student,
                    'total': total,
                    'present': present,
                    'absent': absent,
                    'late': late,
                    'pct': pct,
                })

        return render(request, self.template_name, {
            'classrooms': classrooms,
            'selected_classroom_id': selected_classroom_id,
            'selected_date_from': selected_date_from,
            'selected_date_to': selected_date_to,
            'summary': summary,
            'page_title': 'Attendance Report',
        })