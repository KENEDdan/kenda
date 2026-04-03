from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.StudentListView.as_view(), name='list'),
    path('enrol/', views.StudentEnrolView.as_view(), name='enrol'),
    path('<uuid:pk>/', views.StudentDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.StudentEditView.as_view(), name='edit'),
]