from django import forms

from accounts.models import CustomUser

from .models import ApplicationRecord, PlacementRecord


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = ApplicationRecord
        fields = ('cover_letter',)
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 6}),
        }


class PlacementForm(forms.ModelForm):
    class Meta:
        model = PlacementRecord
        fields = ('company_supervisor', 'placement_date')
        widgets = {
            'placement_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company_supervisor'].queryset = CustomUser.objects.filter(
            role=CustomUser.ROLE_COMPANY_SUPERVISOR
        ).order_by('username')
        self.fields['company_supervisor'].required = False


class ApplicationDecisionForm(forms.Form):
    decision = forms.ChoiceField(choices=[('approved', 'Approve'), ('rejected', 'Reject')])
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4}), label='Optional note')
