from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CompanyProfile, CustomUser, StudentProfile


class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)
    student_number = forms.CharField(required=False, max_length=50)
    course = forms.CharField(required=False, max_length=120)
    department = forms.CharField(required=False, max_length=120)
    company_name = forms.CharField(required=False, max_length=150)
    contact_person = forms.CharField(required=False, max_length=120)
    office_address = forms.CharField(required=False, max_length=250)

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'role',
            'student_number',
            'course',
            'department',
            'company_name',
            'contact_person',
            'office_address',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            choice for choice in CustomUser.ROLE_CHOICES
            if choice[0] != CustomUser.ROLE_COORDINATOR
        ]
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['role'].widget.attrs['class'] = 'form-select'
        self.fields['username'].widget.attrs['autocomplete'] = 'username'
        self.fields['email'].widget.attrs['autocomplete'] = 'email'
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        if role == CustomUser.ROLE_STUDENT:
            if not cleaned_data.get('student_number'):
                self.add_error('student_number', 'Student ID is required for students.')
            if not cleaned_data.get('course'):
                self.add_error('course', 'Program/course is required for students.')
        elif role == CustomUser.ROLE_COMPANY_SUPERVISOR:
            if not cleaned_data.get('company_name'):
                self.add_error('company_name', 'Company name is required for company supervisors.')
            if not cleaned_data.get('contact_person'):
                self.add_error('contact_person', 'Position/contact person is required for company supervisors.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        user.role = role
        if commit:
            user.save()
            if role == CustomUser.ROLE_STUDENT:
                StudentProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        'student_number': self.cleaned_data.get('student_number', ''),
                        'course': self.cleaned_data.get('course', ''),
                        'department': self.cleaned_data.get('department', ''),
                    },
                )
            elif role == CustomUser.ROLE_COMPANY_SUPERVISOR:
                profile, _ = CompanyProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        'company_name': self.cleaned_data.get('company_name', ''),
                        'contact_person': self.cleaned_data.get('contact_person', ''),
                        'office_address': self.cleaned_data.get('office_address', ''),
                    },
                )
                # Keep the coordinator-facing posting record in sync with the
                # self-registered company account, so a supervisor signing up
                # actually shows up as a selectable company when a coordinator
                # creates an internship posting.
                from internships.models import CompanyPosting
                CompanyPosting.objects.update_or_create(
                    linked_profile=profile,
                    defaults={
                        'name': profile.company_name or user.username,
                        'contact_email': user.email,
                    },
                )
        return user


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ('student_number', 'course', 'department')


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ('company_name', 'contact_person', 'office_address')
