from django.core.paginator import Paginator
from django.shortcuts import render

from accounts.decorators import role_login_required
from accounts.models import CustomUser

from .models import AuditLog


@role_login_required(CustomUser.ROLE_COORDINATOR)
def activity_log(request):
    logs = AuditLog.objects.select_related('user').all()
    search_query = request.GET.get('search', '').strip()
    action_filter = request.GET.get('action', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if search_query:
        logs = logs.filter(path__icontains=search_query) | logs.filter(
            user__username__icontains=search_query
        )
    if action_filter:
        logs = logs.filter(action=action_filter)
    if status_filter == 'success':
        logs = logs.filter(status_code__lt=400)
    elif status_filter == 'error':
        logs = logs.filter(status_code__gte=400)

    paginator = Paginator(logs, 25)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'auditlog/activity_log.html', {
        'logs': page,
        'search_query': search_query,
        'action_filter': action_filter,
        'status_filter': status_filter,
        'action_choices': AuditLog.objects.values_list('action', flat=True).distinct().order_by('action'),
        'total_logs': logs.count(),
    })
