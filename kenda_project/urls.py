from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts.views import dashboard_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', dashboard_redirect, name='dashboard'),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('students/', include('apps.students.urls', namespace='students')),
    path('school/', include('apps.school.urls', namespace='school')),
    path('', include('apps.public.urls', namespace='public')),
    path('teachers/', include('apps.teachers.urls', namespace='teachers')),
    path('academics/', include('apps.academics.urls', namespace='academics')),
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),
    path('fees/', include('apps.fees.urls', namespace='fees')),
    path('communications/', include('apps.communications.urls', namespace='communications')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns

    