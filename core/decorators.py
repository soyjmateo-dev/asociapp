from functools import wraps
from django.shortcuts import redirect


def tenant_login_required(view_func):
    """
    Verifica que exista request.organizacion
    y que el usuario esté autenticado.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("tenant_login")

        if not hasattr(request, "organizacion"):
            return redirect("tenant_login")

        return view_func(request, *args, **kwargs)

    return _wrapped_view