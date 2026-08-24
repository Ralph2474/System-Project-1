from django import forms
from django.core.exceptions import ValidationError

from .models import SubmittedDocument


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = SubmittedDocument
        fields = ('document_type', 'file')
        widgets = {
            'file': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 10MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in allowed_extensions:
                raise ValidationError("Only PDF and Word documents are allowed.")
        
        return file


class DocumentDecisionForm(forms.Form):
    decision = forms.ChoiceField(choices=[('validated', 'Validate'), ('rejected', 'Reject')])
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label='Validation note')
