from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.TeacherListView.as_view(), name='list'),
    path('add/', views.TeacherAddView.as_view(), name='add'),
    path('export/', views.TeacherExportView.as_view(), name='export'),
    path('<uuid:pk>/', views.TeacherDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.TeacherEditView.as_view(), name='edit'),
    path('<uuid:pk>/delete/', views.TeacherDeleteView.as_view(), name='delete'),
    path('<uuid:pk>/status/', views.TeacherStatusChangeView.as_view(), name='status'),
    path('credentials/', views.TeacherCredentialsView.as_view(), name='credentials'),
    path('<uuid:pk>/id-card/', views.TeacherIDCardView.as_view(), name='id_card'),
]