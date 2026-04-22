from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    # Subjects
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/add/', views.SubjectCreateView.as_view(), name='subject_add'),
    path('subjects/<int:pk>/edit/', views.SubjectEditView.as_view(), name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.SubjectDeleteView.as_view(), name='subject_delete'),

    # Classes
    path('classes/', views.ClassRoomListView.as_view(), name='class_list'),
    path('classes/add/', views.ClassRoomCreateView.as_view(), name='class_add'),
    path('classes/<int:pk>/', views.ClassRoomDetailView.as_view(), name='class_detail'),
    path('classes/<int:pk>/edit/', views.ClassRoomEditView.as_view(), name='class_edit'),
    path('classes/<int:pk>/delete/', views.ClassRoomDeleteView.as_view(), name='class_delete'),
    path('classes/<int:pk>/assign-subject/', views.SubjectAssignView.as_view(), name='assign_subject'),
    path('assignments/<int:pk>/delete/', views.SubjectAssignDeleteView.as_view(), name='assignment_delete'),

    # Terms
    path('terms/', views.TermListView.as_view(), name='term_list'),
    path('terms/add/', views.TermCreateView.as_view(), name='term_add'),
    path('terms/<int:pk>/edit/', views.TermEditView.as_view(), name='term_edit'),
]