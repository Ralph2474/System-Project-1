from .models import AuditLog


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated and not request.path.startswith('/static/'):
            action = 'READ' if request.method in {'GET', 'HEAD', 'OPTIONS'} else request.method
            AuditLog.objects.create(
                user=user,
                action=action,
                method=request.method,
                path=request.path[:500],
                status_code=response.status_code,
                ip_address=self._get_client_ip(request),
            )

        return response

    @staticmethod
    def _get_client_ip(request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
