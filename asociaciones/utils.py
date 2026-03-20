from django.shortcuts import redirect
from functools import wraps


def tenant_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, slug, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/{slug}/login/")
        return view_func(request, slug, *args, **kwargs)
    return wrapper