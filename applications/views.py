from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.decorators import coordinator_required, role_login_required
from accounts.models import CustomUser
from internships.models import InternshipPosting

from .forms import ApplicationDecisionForm, ApplicationForm, PlacementForm
from .models import ApplicationRecord, PlacementRecord


@role_login_required(CustomUser.ROLE_STUDENT)
def application_list(request):
    # Get base queryset
    applications = ApplicationRecord.objects.select_related('student', 'internship').filter(student=request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        applications = applications.filter(
            internship__title__icontains=search_query) | applications.filter(
            internship__company__name__icontains=search_query)
    
    # Filtering by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'applied_on')
    if sort_by == 'applied_on':
        applications = applications.order_by('-applied_on')
    elif sort_by == 'title':
        applications = applications.order_by('internship__title')
    elif sort_by == 'status':
        applications = applications.order_by('status', '-applied_on')
    
    # Pagination
    paginator = Paginator(applications, 10)  # 10 items per page
    page = request.GET.get('page', 1)
    
    try:
        applications = paginator.page(page)
    except PageNotAnInteger:
        applications = paginator.page(1)
    except EmptyPage:
        applications = paginator.page(paginator.num_pages)
    
    context = {
        'applications': applications,
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
    }
    return render(request, 'applications/application_list.html', context)


@role_login_required(CustomUser.ROLE_STUDENT)
def apply_to_internship(request, pk):
    internship = get_object_or_404(InternshipPosting, pk=pk)

    if PlacementRecord.objects.filter(student=request.user).exists():
        messages.error(request, 'You already have an active placement and cannot apply to another posting.')
        return redirect('applications:application_list')

    if ApplicationRecord.objects.filter(student=request.user, internship=internship).exists():
        messages.error(request, 'You already submitted an application for this posting.')
        return redirect('applications:application_list')

    if not internship.is_open:
        messages.error(request, 'This posting is no longer open for applications.')
        return redirect('internships:posting_list')

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            ApplicationRecord.objects.create(
                student=request.user,
                internship=internship,
                cover_letter=form.cleaned_data['cover_letter'],
                status=ApplicationRecord.STATUS_PENDING,
            )
            messages.success(request, 'Application submitted successfully.')
            return redirect('applications:application_list')
    else:
        form = ApplicationForm()
    return render(request, 'applications/apply_form.html', {'form': form, 'internship': internship})


@role_login_required(CustomUser.ROLE_STUDENT)
def application_withdraw(request, pk):
    application = get_object_or_404(ApplicationRecord, pk=pk, student=request.user)
    if request.method != 'POST':
        return redirect('applications:application_list')
    if application.status != ApplicationRecord.STATUS_PENDING:
        messages.error(request, 'Only pending applications can be withdrawn.')
    else:
        application.delete()
        messages.success(request, 'Application withdrawn successfully.')
    return redirect('applications:application_list')


@role_login_required(CustomUser.ROLE_COORDINATOR)
def application_manage(request):
    # Get base queryset
    applications = ApplicationRecord.objects.select_related('student', 'internship').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        applications = applications.filter(
            student__username__icontains=search_query) | applications.filter(
            internship__title__icontains=search_query) | applications.filter(
            internship__company__name__icontains=search_query)
    
    # Filtering by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'applied_on')
    if sort_by == 'applied_on':
        applications = applications.order_by('-applied_on')
    elif sort_by == 'title':
        applications = applications.order_by('internship__title')
    elif sort_by == 'student':
        applications = applications.order_by('student__username')
    elif sort_by == 'status':
        applications = applications.order_by('status', '-applied_on')
    
    # Pagination
    paginator = Paginator(applications, 15)  # 15 items per page for coordinators
    page = request.GET.get('page', 1)
    
    try:
        applications = paginator.page(page)
    except PageNotAnInteger:
        applications = paginator.page(1)
    except EmptyPage:
        applications = paginator.page(paginator.num_pages)

    # Attach each approved application's placement (if any) so the template
    # can link straight to the "assign supervisor" page.
    placements = PlacementRecord.objects.filter(
        student_id__in=[a.student_id for a in applications],
        internship_id__in=[a.internship_id for a in applications],
    )
    placement_by_key = {(p.student_id, p.internship_id): p for p in placements}
    for application in applications:
        placement = placement_by_key.get((application.student_id, application.internship_id))
        application.placement_id_for_manage = placement.id if placement else None
        application.placement_has_supervisor = bool(placement and placement.company_supervisor_id)

    context = {
        'applications': applications,
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
    }
    return render(request, 'applications/application_manage.html', context)


@coordinator_required
def placement_update(request, pk):
    placement = get_object_or_404(PlacementRecord, pk=pk)
    if request.method == 'POST':
        form = PlacementForm(request.POST, instance=placement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Placement updated successfully.')
            return redirect('applications:application_manage')
    else:
        form = PlacementForm(instance=placement)
    return render(request, 'applications/placement_form.html', {'form': form, 'placement': placement})


@role_login_required(CustomUser.ROLE_COORDINATOR)
def application_decide(request, pk):
    application = get_object_or_404(ApplicationRecord, pk=pk)
    if application.status != ApplicationRecord.STATUS_PENDING:
        messages.info(request, 'This application has already been processed.')
        return redirect('applications:application_manage')

    if request.method == 'POST':
        form = ApplicationDecisionForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data['decision']
            note = form.cleaned_data['note']
            internship = application.internship
            with transaction.atomic():
                if decision == ApplicationRecord.STATUS_APPROVED:
                    if internship.slots_available <= 0:
                        messages.error(request, 'This posting has no available slots left.')
                        return redirect('applications:application_manage')
                    application.status = ApplicationRecord.STATUS_APPROVED
                    application.decision_note = note
                    application.save()
                    internship.slots_available -= 1
                    internship.save(update_fields=['slots_available'])
                    PlacementRecord.objects.update_or_create(
                        student=application.student,
                        internship=internship,
                        defaults={'placement_date': timezone.localdate()},
                    )
                    messages.success(request, 'Application approved and placement created.')
                else:
                    application.status = ApplicationRecord.STATUS_REJECTED
                    application.decision_note = note
                    application.save()
                    messages.success(request, 'Application rejected.')
            # Preserve filters when redirecting
            search_query = request.POST.get('search', '')
            status_filter = request.POST.get('status', '')
            sort_by = request.POST.get('sort', 'applied_on')
            page = request.POST.get('page', '1')
            redirect_url = f"?search={search_query}&status={status_filter}&sort={sort_by}&page={page}"
            return redirect(f"{reverse('applications:application_manage')}{redirect_url}")
    else:
        form = ApplicationDecisionForm()
    return render(request, 'applications/application_manage.html', {'applications': ApplicationRecord.objects.filter(status=ApplicationRecord.STATUS_PENDING), 'form': form, 'application': application})
