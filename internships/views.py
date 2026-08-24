from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_login_required
from accounts.models import CustomUser

from .forms import CompanyPostingForm, InternshipPostingForm
from .models import CompanyPosting, InternshipPosting


@role_login_required(CustomUser.ROLE_STUDENT, CustomUser.ROLE_COORDINATOR)
def internship_list(request):
    # Get base queryset based on user role
    if request.user.role == CustomUser.ROLE_COORDINATOR:
        postings = InternshipPosting.objects.select_related('company').all()
    else:
        postings = InternshipPosting.objects.select_related('company').filter(
            is_active=True,
            slots_available__gt=0,
        ).exclude(deadline__lt=timezone.localdate())
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        postings = postings.filter(
            title__icontains=search_query) | postings.filter(
            company__name__icontains=search_query) | postings.filter(
            location__icontains=search_query)
    
    # Filtering functionality
    location_filter = request.GET.get('location', '')
    if location_filter:
        postings = postings.filter(location__icontains=location_filter)
    
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        postings = postings.filter(is_active=True)
    elif status_filter == 'inactive':
        postings = postings.filter(is_active=False)
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'deadline')
    if sort_by == 'deadline':
        postings = postings.order_by('-deadline', '-updated_at')
    elif sort_by == 'title':
        postings = postings.order_by('title')
    elif sort_by == 'company':
        postings = postings.order_by('company__name')
    elif sort_by == 'updated':
        postings = postings.order_by('-updated_at')

    total_postings = postings.count()
    open_postings = postings.filter(is_active=True, slots_available__gt=0).exclude(
        deadline__lt=timezone.localdate()
    ).count()
    
    # Pagination
    paginator = Paginator(postings, 10)  # 10 items per page
    page = request.GET.get('page', 1)
    
    try:
        postings = paginator.page(page)
    except PageNotAnInteger:
        postings = paginator.page(1)
    except EmptyPage:
        postings = paginator.page(paginator.num_pages)
    
    context = {
        'postings': postings,
        'search_query': search_query,
        'location_filter': location_filter,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'total_postings': total_postings,
        'open_postings': open_postings,
    }
    return render(request, 'internships/posting_list.html', context)


@role_login_required(CustomUser.ROLE_COORDINATOR)
def internship_report(request):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Internship Postings'

    headers = [
        'Title',
        'Company',
        'Location',
        'Duration',
        'Required Hours',
        'Slots Available',
        'Deadline',
        'Status',
        'Created By',
        'Last Updated',
    ]
    worksheet.append(headers)

    header_fill = PatternFill(fill_type='solid', fgColor='0F2747')
    for cell in worksheet[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = header_fill

    postings = InternshipPosting.objects.select_related('company', 'created_by').order_by('-deadline', 'title')
    for posting in postings:
        worksheet.append([
            posting.title,
            posting.company.name,
            posting.location,
            posting.duration,
            posting.required_hours,
            posting.slots_available,
            posting.deadline,
            'Open' if posting.is_open else 'Closed',
            posting.created_by.username if posting.created_by else '',
            posting.updated_at.replace(tzinfo=None),
        ])

    worksheet.freeze_panes = 'A2'
    worksheet.auto_filter.ref = worksheet.dimensions
    column_widths = {
        'A': 28, 'B': 24, 'C': 20, 'D': 16, 'E': 16,
        'F': 16, 'G': 14, 'H': 12, 'I': 18, 'J': 22,
    }
    for column, width in column_widths.items():
        worksheet.column_dimensions[column].width = width

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="internship_postings_{timestamp}.xlsx"'
    workbook.save(response)
    return response


@role_login_required(CustomUser.ROLE_STUDENT, CustomUser.ROLE_COORDINATOR)
def internship_detail(request, pk):
    posting = get_object_or_404(InternshipPosting, pk=pk)
    if request.user.role == CustomUser.ROLE_STUDENT and not posting.is_open:
        return render(request, 'internships/posting_detail.html', {'posting': None})
    return render(request, 'internships/posting_detail.html', {'posting': posting})


@role_login_required(CustomUser.ROLE_COORDINATOR)
def internship_create(request):
    if request.method == 'POST':
        form = InternshipPostingForm(request.POST)
        if form.is_valid():
            posting = form.save(commit=False)
            posting.created_by = request.user
            posting.save()
            messages.success(request, 'Posting created successfully.')
            return redirect('internships:posting_detail', pk=posting.pk)
    else:
        form = InternshipPostingForm()
    return render(request, 'internships/posting_form.html', {'form': form, 'posting': None})


@role_login_required(CustomUser.ROLE_COORDINATOR)
def internship_update(request, pk):
    posting = get_object_or_404(InternshipPosting, pk=pk)
    if request.method == 'POST':
        form = InternshipPostingForm(request.POST, instance=posting)
        if form.is_valid():
            form.save()
            messages.success(request, 'Posting updated successfully.')
            return redirect('internships:posting_detail', pk=posting.pk)
    else:
        form = InternshipPostingForm(instance=posting)
    return render(request, 'internships/posting_form.html', {'form': form, 'posting': posting})


@role_login_required(CustomUser.ROLE_COORDINATOR)
def internship_delete(request, pk):
    posting = get_object_or_404(InternshipPosting, pk=pk)
    if request.method != 'POST':
        return redirect('internships:posting_detail', pk=posting.pk)

    if posting.applications.exists() or posting.placements.exists():
        messages.error(request, 'This posting cannot be deleted because it has applications or placements.')
    else:
        posting.delete()
        messages.success(request, 'Posting deleted successfully.')
        return redirect('internships:posting_list')

    return redirect('internships:posting_detail', pk=posting.pk)


@role_login_required(CustomUser.ROLE_COORDINATOR)
def company_create(request):
    if request.method == 'POST':
        form = CompanyPostingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company created successfully.')
            return redirect('internships:posting_list')
    else:
        form = CompanyPostingForm()
    return render(request, 'internships/company_form.html', {'form': form})
