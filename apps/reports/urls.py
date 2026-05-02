from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportsDashboardView.as_view(), name='dashboard'),
    path('students/', views.StudentReportView.as_view(), name='students'),
    path('attendance/', views.AttendanceReportView.as_view(), name='attendance'),
    path('fees/', views.FinancialReportView.as_view(), name='fees'),
    path('export/students/', views.ExportStudentSummaryView.as_view(), name='export_students'),
]