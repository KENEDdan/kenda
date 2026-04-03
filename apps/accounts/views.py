from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def dashboard_redirect(request):
    """Send each user to the right dashboard based on their role."""
    user = request.user

    if user.is_superuser or user.role == 'admin':
        return redirect('dashboard:admin')
    elif user.role == 'teacher':
        return redirect('dashboard:teacher')
    elif user.role == 'student':
        return redirect('dashboard:student')
    elif user.role == 'parent':
        return redirect('dashboard:parent')
    else:
        return redirect('dashboard:staff')