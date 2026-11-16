from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from accounts.decorators import role_login_required
from accounts.models import CustomUser
from applications.models import PlacementRecord

from .forms import DailyTimeLogForm
from .models import DailyTimeLog


def _parse_date(value):
    try:
        return parse_date(value) if value else None
    except ValueError:  # well-formed but impossible, e.g. 2026-02-31
        return None


@role_login_required(CustomUser.ROLE_STUDENT)
def time_log_list(request):
    placement = PlacementRecord.objects.filter(student=request.user).select_related('internship').first()
    entries = DailyTimeLog.objects.filter(student=request.user).order_by('-entry_date')

    total_hours = DailyTimeLog.get_student_hours(request.user)
    required_hours = (
        placement.internship.required_hours
        if placement and placement.internship
        else DailyTimeLog.REQUIRED_HOURS
    )
    progress_percent = round((total_hours / required_hours) * 100) if required_hours else 0
    progress_percent = min(progress_percent, 100)
    remaining_hours = max(required_hours - total_hours, 0)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        entries = entries.filter(accomplishment__icontains=search_query)
    
    # Date range filtering
    # Ignore malformed dates instead of crashing with a 500.
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    parsed_from = _parse_date(date_from)
    parsed_to = _parse_date(date_to)
    if parsed_from:
        entries = entries.filter(entry_date__gte=parsed_from)
    else:
        date_from = ''
    if parsed_to:
        entries = entries.filter(entry_date__lte=parsed_to)
    else:
        date_to = ''
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'entry_date')
    if sort_by == 'entry_date':
        entries = entries.order_by('-entry_date')
    elif sort_by == 'hours':
        entries = entries.order_by('-hours_completed')
    elif sort_by == 'date_asc':
        entries = entries.order_by('entry_date')
    
    # Pagination
    paginator = Paginator(entries, 15)  # 15 items per page
    page = request.GET.get('page', 1)
    
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    context = {
        'entries': entries,
        'progress_percent': progress_percent,
        'total_hours': total_hours,
        'required_hours': required_hours,
        'remaining_hours': remaining_hours,
        'placement': placement,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
    }
    return render(request, 'timelog/timelog_list.html', context)


@role_login_required(CustomUser.ROLE_STUDENT)
def time_log_form(request):
    placement = PlacementRecord.objects.filter(student=request.user).first()
    if placement is None:
        messages.info(request, 'You can log time once you have been placed in an internship.')
        return redirect('timelog:time_log_list')
    if request.method == 'POST':
        form = DailyTimeLogForm(request.POST, placement=placement)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.student = request.user
            entry.save()
            messages.success(request, 'Time log entry saved successfully.')
            return redirect('timelog:time_log_list')
    else:
        form = DailyTimeLogForm(placement=placement)

    return render(request, 'timelog/timelog_form.html', {'form': form, 'entry': None, 'placement': placement})


@role_login_required(CustomUser.ROLE_STUDENT)
def time_log_update(request, pk):
    entry = get_object_or_404(DailyTimeLog, pk=pk, student=request.user)
    placement = PlacementRecord.objects.filter(student=request.user).first()
    if placement is None:
        messages.info(request, 'You can edit time logs once you have been placed in an internship.')
        return redirect('timelog:time_log_list')
    if request.method == 'POST':
        form = DailyTimeLogForm(request.POST, instance=entry, placement=placement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Time log updated successfully.')
            return redirect('timelog:time_log_list')
    else:
        form = DailyTimeLogForm(instance=entry, placement=placement)

    return render(request, 'timelog/timelog_form.html', {'form': form, 'entry': entry, 'placement': placement})


@role_login_required(CustomUser.ROLE_STUDENT)
def time_log_delete(request, pk):
    entry = get_object_or_404(DailyTimeLog, pk=pk, student=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Time log entry deleted successfully.')
    return redirect('timelog:time_log_list')