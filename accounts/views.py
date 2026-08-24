from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .decorators import role_login_required
from .forms import CompanyProfileForm, RegistrationForm, StudentProfileForm
from .models import CompanyProfile, CustomUser, StudentProfile


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # role_dashboard already renders the right view per-role, so every
        # login lands on the same URL regardless of the user's role.
        return reverse_lazy('dashboard:role_dashboard')


@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:landing')


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard:role_dashboard')
    return render(request, 'accounts/landing.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:role_dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('dashboard:role_dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@role_login_required(CustomUser.ROLE_STUDENT)
def student_profile(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:student_profile')
    else:
        form = StudentProfileForm(instance=profile)
    return render(request, 'accounts/student_profile.html', {'form': form, 'user': request.user})


@role_login_required(CustomUser.ROLE_COMPANY_SUPERVISOR)
def company_profile(request):
    profile, created = CompanyProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # Keep the linked posting record (used when coordinators create
            # internship postings) in sync with any profile edits.
            from internships.models import CompanyPosting
            CompanyPosting.objects.update_or_create(
                linked_profile=profile,
                defaults={
                    'name': profile.company_name or request.user.username,
                    'contact_email': request.user.email,
                },
            )
            messages.success(request, 'Company profile updated.')
            return redirect('accounts:company_profile')
    else:
        form = CompanyProfileForm(instance=profile)
    return render(request, 'accounts/company_profile.html', {'form': form, 'user': request.user})
