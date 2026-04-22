from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import SchoolProfile
from .forms import SchoolProfileForm


from django.urls import reverse_lazy

@method_decorator(login_required, name='dispatch')
class SchoolSettingsView(UpdateView):
    model = SchoolProfile
    form_class = SchoolProfileForm
    template_name = 'school/settings.html'
    success_url = reverse_lazy('dashboard:admin')  # ← change this line

    def get_object(self):
        return SchoolProfile.get()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'School Settings'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'School settings saved successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please fix the errors below.')
        return super().form_invalid(form)