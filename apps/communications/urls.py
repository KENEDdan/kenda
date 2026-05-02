from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.AnnouncementListView.as_view(), name='list'),
    path('create/', views.AnnouncementCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AnnouncementDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.AnnouncementEditView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.AnnouncementDeleteView.as_view(), name='delete'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', views.MarkReadView.as_view(), name='mark_read'),
    path('notifications/read-all/', views.MarkAllReadView.as_view(), name='mark_all_read'),
]