from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin/', views.AdminDashboardView.as_view(), name='admin'),
    path('teacher/', views.TeacherDashboardView.as_view(), name='teacher'),
    path('student/', views.StudentDashboardView.as_view(), name='student'),
    path('parent/', views.ParentDashboardView.as_view(), name='parent'),
    path('staff/', views.StaffDashboardView.as_view(), name='staff'),
]