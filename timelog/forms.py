from datetime import datetime, timedelta

from django import forms
from django.core.exceptions import ValidationError

from .models import DailyTimeLog


class DailyTimeLogForm(forms.ModelForm):
    class Meta:
        model = DailyTimeLog
        fields = ('entry_date', 'time_in', 'time_out', 'accomplishment')
        widgets = {
            'entry_date': forms.DateInput(attrs={'type': 'date'}),
            'time_in': forms.TimeInput(attrs={'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'type': 'time'}),
            'accomplishment': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, placement=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.placement = placement

    def clean(self):
        cleaned_data = super().clean()
        time_in = cleaned_data.get('time_in')
        time_out = cleaned_data.get('time_out')
        entry_date = cleaned_data.get('entry_date')

        if time_in and time_out and entry_date:
            # Convert time strings to datetime objects for calculation
            time_in_dt = datetime.combine(entry_date, time_in)
            time_out_dt = datetime.combine(entry_date, time_out)

            # Handle overnight case (time_out is next day)
            if time_out_dt < time_in_dt:
                time_out_dt += timedelta(days=1)

            # Calculate hours
            time_diff = time_out_dt - time_in_dt
            hours = round(time_diff.total_seconds() / 3600, 2)

            # Validate reasonable working hours (max 24 hours per day)
            if hours > 24:
                raise ValidationError("Time entries cannot exceed 24 hours in a single day.")

            # Validate minimum working hours (at least 0.5 hours)
            if hours < 0.5:
                raise ValidationError("Time entries must be at least 30 minutes.")

            cleaned_data['hours_completed'] = hours

        if (
            self.placement
            and self.placement.placement_date
            and entry_date
            and entry_date < self.placement.placement_date
        ):
            raise ValidationError('You cannot log time before the placement start date.')

        if self.placement and entry_date:
            duplicate_exists = DailyTimeLog.objects.filter(
                student=self.placement.student,
                entry_date=entry_date,
            ).exclude(pk=self.instance.pk if self.instance and self.instance.pk else None).exists()
            if duplicate_exists:
                raise ValidationError('A time log entry already exists for this date.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Auto-calculate hours if time_in and time_out are provided
        if self.cleaned_data.get('time_in') and self.cleaned_data.get('time_out'):
            instance.hours_completed = self.cleaned_data['hours_completed']

        if commit:
            instance.save()
        return instance