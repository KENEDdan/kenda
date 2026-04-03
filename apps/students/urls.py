from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.StudentListView.as_view(), name='list'),
    path('enrol/', views.StudentEnrolView.as_view(), name='enrol'),
    path('import/', views.StudentImportView.as_view(), name='import'),
    path('promote/', views.BulkPromotionView.as_view(), name='bulk_promote'),
    path('<uuid:pk>/', views.StudentDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.StudentEditView.as_view(), name='edit'),
    path('<uuid:pk>/status/', views.StudentStatusChangeView.as_view(), name='status'),
    path('<uuid:pk>/delete/', views.StudentDeleteView.as_view(), name='delete'),
    path('<uuid:pk>/id-card/', views.StudentIDCardView.as_view(), name='id_card'),
    path('<uuid:pk>/promote/', views.StudentPromoteView.as_view(), name='promote'),
    path('<uuid:pk>/history/', views.StudentHistoryView.as_view(), name='history'),
]