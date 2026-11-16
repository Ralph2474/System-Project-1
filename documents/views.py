import os

from django.contrib import messages
from django.http import FileResponse, Http404
from django.utils.http import urlencode
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import coordinator_required, role_login_required
from accounts.models import CustomUser

from .forms import DocumentDecisionForm, DocumentUploadForm
from .models import SubmittedDocument


@role_login_required(CustomUser.ROLE_STUDENT)
def document_list(request):
    # Get base queryset
    documents = SubmittedDocument.objects.select_related('student').filter(student=request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        documents = documents.filter(document_type__icontains=search_query)
    
    # Filtering by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        documents = documents.filter(status=status_filter)
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'uploaded_on')
    if sort_by == 'uploaded_on':
        documents = documents.order_by('-uploaded_on')
    elif sort_by == 'type':
        documents = documents.order_by('document_type')
    elif sort_by == 'status':
        documents = documents.order_by('status', '-uploaded_on')
    
    # Pagination
    paginator = Paginator(documents, 10)  # 10 items per page
    page = request.GET.get('page', 1)
    
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)
    
    context = {
        'documents': documents,
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
    }
    return render(request, 'documents/document_list.html', context)


@role_login_required(CustomUser.ROLE_STUDENT)
def document_upload(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.student = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('documents:document_list')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'documents/document_form.html', {'form': form})


@role_login_required(CustomUser.ROLE_STUDENT)
def document_delete(request, pk):
    document = get_object_or_404(SubmittedDocument, pk=pk, student=request.user)
    if request.method != 'POST':
        return redirect('documents:document_list')
    if document.status == SubmittedDocument.STATUS_VALIDATED:
        messages.error(request, 'Validated documents cannot be deleted.')
    else:
        if document.file:
            document.file.delete(save=False)
        document.delete()
        messages.success(request, 'Document deleted successfully.')
    return redirect('documents:document_list')


@coordinator_required
def document_validate(request):
    # Get base queryset
    documents = SubmittedDocument.objects.select_related('student').filter(status=SubmittedDocument.STATUS_PENDING)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        documents = documents.filter(
            student__username__icontains=search_query) | documents.filter(
            document_type__icontains=search_query)
    
    # Sorting functionality
    sort_by = request.GET.get('sort', 'uploaded_on')
    if sort_by == 'uploaded_on':
        documents = documents.order_by('-uploaded_on')
    elif sort_by == 'student':
        documents = documents.order_by('student__username')
    elif sort_by == 'type':
        documents = documents.order_by('document_type')
    
    # Pagination
    paginator = Paginator(documents, 15)  # 15 items per page for coordinators
    page = request.GET.get('page', 1)
    
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)
    
    context = {
        'documents': documents,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'documents/document_validate.html', context)


@role_login_required(CustomUser.ROLE_COORDINATOR)
def document_decide(request, pk):
    document = get_object_or_404(SubmittedDocument, pk=pk)
    if request.method == 'POST':
        form = DocumentDecisionForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data['decision']
            note = form.cleaned_data['note']
            document.status = decision
            document.validation_note = note
            document.save()
            messages.success(request, f'Document marked as {decision}.')
            # Preserve filters when redirecting
            search_query = request.POST.get('search', '')
            sort_by = request.POST.get('sort', 'uploaded_on')
            page = request.POST.get('page', '1')
            query = urlencode({'search': search_query, 'sort': sort_by, 'page': page})
            return redirect(f"{reverse('documents:document_validate')}?{query}")
    else:
        form = DocumentDecisionForm()
    return render(request, 'documents/document_validate.html', {'documents': SubmittedDocument.objects.filter(status=SubmittedDocument.STATUS_PENDING), 'form': form, 'document': document})


@role_login_required(CustomUser.ROLE_STUDENT, CustomUser.ROLE_COORDINATOR)
def document_file(request, pk):
    """Stream an uploaded document to its owner or a coordinator.

    Files are served through this view instead of a public /media/ URL so that
    they stay private and also work when DEBUG=False (Django does not serve
    MEDIA_URL in production)."""
    document = get_object_or_404(SubmittedDocument, pk=pk)
    if request.user.role == CustomUser.ROLE_STUDENT and document.student_id != request.user.pk:
        raise Http404
    if not document.file:
        raise Http404
    try:
        handle = document.file.open('rb')
    except FileNotFoundError:
        raise Http404
    return FileResponse(handle, filename=os.path.basename(document.file.name))
