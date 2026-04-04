from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    path('settings/', views.SchoolSettingsView.as_view(), name='settings'),
]