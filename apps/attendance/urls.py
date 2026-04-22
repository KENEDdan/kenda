from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.AttendanceDashboardView.as_view(), name='dashboard'),
    path('mark/<int:classroom_pk>/', views.MarkAttendanceView.as_view(), name='mark'),
    path('view/<int:classroom_pk>/', views.AttendanceHistoryView.as_view(), name='history'),
    path('student/<uuid:student_pk>/', views.StudentAttendanceView.as_view(), name='student'),
    path('report/', views.AttendanceReportView.as_view(), name='report'),
]