from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class KendaAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        data = form.cleaned_data
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.role = 'admin'
        if commit:
            user.save()
        return user

    def get_login_redirect_url(self, request):
        return '/dashboard/'