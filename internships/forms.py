from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import CompanyPosting, InternshipPosting


class CompanyPostingForm(forms.ModelForm):
    class Meta:
        model = CompanyPosting
        fields = ('name', 'contact_email', 'description')


class InternshipPostingForm(forms.ModelForm):
    class Meta:
        model = InternshipPosting
        fields = (
            'company',
            'title',
            'location',
            'duration',
            'description',
            'required_hours',
            'slots_available',
            'deadline',
            'is_active',
        )
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 6}),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.localdate():
            raise ValidationError('Deadline cannot be in the past.')
        return deadline

    def clean_slots_available(self):
        slots_available = self.cleaned_data.get('slots_available')
        if slots_available is not None and slots_available <= 0:
            raise ValidationError('Slots available must be greater than 0.')
        return slots_available

    def clean_required_hours(self):
        required_hours = self.cleaned_data.get('required_hours')
        if required_hours is not None and required_hours <= 0:
            raise ValidationError('Required hours must be greater than 0.')
        return required_hours
