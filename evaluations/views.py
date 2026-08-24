from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_login_required
from accounts.models import CustomUser
from applications.models import PlacementRecord

from .forms import EvaluationRecordForm
from .models import EvaluationRecord


@role_login_required(CustomUser.ROLE_STUDENT, CustomUser.ROLE_COMPANY_SUPERVISOR, CustomUser.ROLE_COORDINATOR)
def evaluation_list(request):
    # Get base queryset based on user role
    if request.user.role == CustomUser.ROLE_STUDENT:
        evaluations = EvaluationRecord.objects.select_related('student', 'supervisor').filter(student=request.user)
    elif request.user.role == CustomUser.ROLE_COMPANY_SUPERVISOR:
        evaluations = EvaluationRecord.objects.select_related('student', 'supervisor').filter(supervisor=request.user)
    else:
        evaluations = EvaluationRecord.objects.select_related('student', 'supervisor').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        evaluations = evaluations.filter(
            student__username__icontains=search_query) | evaluations.filter(
            supervisor__username__icontains=search_query)
    
    # Filtering by rating
    rating_filter = request.GET.get('rating', '')
    if rating_filter:
        evaluations = evaluations.filter(rating=rating_filter)
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'submitted_on')
    if sort_by == 'submitted_on':
        evaluations = evaluations.order_by('-submitted_on')
    elif sort_by == 'rating':
        evaluations = evaluations.order_by('-rating')
    elif sort_by == 'student':
        evaluations = evaluations.order_by('student__username')
    elif sort_by == 'supervisor':
        evaluations = evaluations.order_by('supervisor__username')
    
    # Pagination
    paginator = Paginator(evaluations, 10)  # 10 items per page
    page = request.GET.get('page', 1)
    
    try:
        evaluations = paginator.page(page)
    except PageNotAnInteger:
        evaluations = paginator.page(1)
    except EmptyPage:
        evaluations = paginator.page(paginator.num_pages)
    
    context = {
        'evaluations': evaluations,
        'search_query': search_query,
        'rating_filter': rating_filter,
        'sort_by': sort_by,
    }
    return render(request, 'evaluations/evaluation_list.html', context)


@role_login_required(CustomUser.ROLE_COMPANY_SUPERVISOR)
def evaluation_form(request, student_id=None):
    placement_students = CustomUser.objects.filter(
        role=CustomUser.ROLE_STUDENT,
        pk__in=PlacementRecord.objects.filter(company_supervisor=request.user).values('student_id'),
    ).order_by('username')

    initial = {}
    if student_id:
        try:
            initial['student'] = placement_students.get(pk=student_id)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Student not found.')
            return redirect('evaluations:evaluation_list')

    if request.method == 'POST':
        form = EvaluationRecordForm(request.POST, available_students=placement_students)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.supervisor = request.user
            try:
                evaluation.save()
            except IntegrityError:
                form.add_error('student', 'An evaluation for this student has already been submitted.')
            else:
                messages.success(request, 'Evaluation submitted successfully.')
                return redirect('evaluations:evaluation_list')
    else:
        form = EvaluationRecordForm(initial=initial, available_students=placement_students)

    return render(request, 'evaluations/evaluation_form.html', {'form': form, 'evaluation': None})


@role_login_required(CustomUser.ROLE_STUDENT, CustomUser.ROLE_COMPANY_SUPERVISOR, CustomUser.ROLE_COORDINATOR)
def evaluation_detail(request, pk):
    evaluation = get_object_or_404(EvaluationRecord, pk=pk)

    if request.user.role == CustomUser.ROLE_STUDENT and evaluation.student != request.user:
        messages.error(request, 'You can only view your own evaluations.')
        return redirect('evaluations:evaluation_list')
    elif request.user.role == CustomUser.ROLE_COMPANY_SUPERVISOR and evaluation.supervisor != request.user:
        messages.error(request, 'You can only view evaluations you submitted.')
        return redirect('evaluations:evaluation_list')

    return render(request, 'evaluations/evaluation_detail.html', {'evaluation': evaluation})


@role_login_required(CustomUser.ROLE_COMPANY_SUPERVISOR)
def evaluation_delete(request, pk):
    evaluation = get_object_or_404(EvaluationRecord, pk=pk, supervisor=request.user)
    if request.method == 'POST':
        evaluation.delete()
        messages.success(request, 'Evaluation deleted successfully.')
    return redirect('evaluations:evaluation_list')