from django import forms
from django.core.exceptions import ValidationError

from accounts.models import CustomUser

from .models import EvaluationRecord


class EvaluationRecordForm(forms.ModelForm):
    class Meta:
        model = EvaluationRecord
        fields = ('student', 'rating', 'punctuality', 'professionalism', 'teamwork', 'comments')
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, available_students=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = available_students or CustomUser.objects.none()

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not 1 <= rating <= 5:
            raise forms.ValidationError('Overall rating must be between 1 and 5.')
        return rating

    def clean_punctuality(self):
        value = self.cleaned_data.get('punctuality')
        if not 1 <= value <= 5:
            raise forms.ValidationError('Punctuality score must be between 1 and 5.')
        return value

    def clean_professionalism(self):
        value = self.cleaned_data.get('professionalism')
        if not 1 <= value <= 5:
            raise forms.ValidationError('Professionalism score must be between 1 and 5.')
        return value

    def clean_teamwork(self):
        value = self.cleaned_data.get('teamwork')
        if not 1 <= value <= 5:
            raise forms.ValidationError('Teamwork score must be between 1 and 5.')
        return value
