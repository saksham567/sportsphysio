from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from accounts.models import User


def staff_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_superuser or user.role == User.Role.STAFF or user.is_staff:
            return view_func(request, *args, **kwargs)
        return redirect("portal:dashboard")

    return wrapper
