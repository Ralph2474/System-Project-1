from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import CustomUser


def role_required(*allowed_roles):
    """Restrict a view to specific roles. Assumes the caller has already
    ensured the user is authenticated (e.g. via login_required) so that
    anonymous users are redirected to the login page rather than shown a
    raw 403."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            if request.user.role not in allowed_roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def role_login_required(*allowed_roles):
    """Require login first (redirecting anonymous users to the login page),
    then enforce the role check. login_required must be the outermost
    wrapper so it runs before role_required's authentication check."""
    def decorator(view_func):
        decorated_view = role_required(*allowed_roles)(view_func)
        decorated_view = login_required(decorated_view)
        return decorated_view
    return decorator


def coordinator_required(view_func):
    """Restrict view to coordinators only, redirecting anonymous users to login."""
    return login_required(role_required(CustomUser.ROLE_COORDINATOR)(view_func))
