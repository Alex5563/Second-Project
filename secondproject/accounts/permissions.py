from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import UserRole

def is_recruiter(user):
    return (user.is_authenticated and
            UserRole.objects.filter(user=user, role=UserRole.RECRUITER).exists())

def job_seeker_required(view):
    """Login required. Recruiters are sent back to the home page."""
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if is_recruiter(request.user):
            return redirect('home.index')
        return view(request, *args, **kwargs)
    return wrapper

def recruiter_required(view):
    """Login required. Job seekers are sent back to the home page."""
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not is_recruiter(request.user):
            return redirect('home.index')
        return view(request, *args, **kwargs)
    return wrapper