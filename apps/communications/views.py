from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import Announcement, Notification
from .forms import AnnouncementForm


@method_decorator(login_required, name='dispatch')
class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'communications/list.html'
    context_object_name = 'announcements'
    paginate_by = 20

    def get_queryset(self):
        return Announcement.objects.select_related(
            'created_by', 'grade'
        ).filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Announcements'
        ctx['total'] = Announcement.objects.filter(is_published=True).count()
        return ctx


@method_decorator(login_required, name='dispatch')
class AnnouncementCreateView(CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'communications/form.html'
    success_url = reverse_lazy('communications:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Create Announcement'
        return ctx

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Announcement published!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = 'communications/detail.html'
    context_object_name = 'announcement'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.object.title
        return ctx


@method_decorator(login_required, name='dispatch')
class AnnouncementEditView(UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'communications/form.html'

    def get_success_url(self):
        return reverse_lazy(
            'communications:detail', kwargs={'pk': self.object.pk}
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Edit — {self.object.title}"
        ctx['is_edit'] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Announcement updated.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class AnnouncementDeleteView(DeleteView):
    model = Announcement
    template_name = 'communications/confirm_delete.html'
    success_url = reverse_lazy('communications:list')
    context_object_name = 'announcement'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Delete Announcement'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Announcement deleted.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class NotificationListView(ListView):
    model = Notification
    template_name = 'communications/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'My Notifications'
        ctx['unread_count'] = Notification.objects.filter(
            user=self.request.user, is_read=False
        ).count()
        return ctx


@method_decorator(login_required, name='dispatch')
class MarkReadView(View):
    def post(self, request, pk):
        notification = get_object_or_404(
            Notification, pk=pk, user=request.user
        )
        notification.is_read = True
        notification.save()
        return redirect('communications:notifications')


@method_decorator(login_required, name='dispatch')
class MarkAllReadView(View):
    def post(self, request):
        Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('communications:notifications')