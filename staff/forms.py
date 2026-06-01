from django import forms

from portal.models import ConsultationHistory, Payment, ProgressEntry, RehabProgram


class PaymentActionForm(forms.Form):
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control", "placeholder": "Optional note"}),
    )


class RehabProgramForm(forms.ModelForm):
    class Meta:
        model = RehabProgram
        fields = ("title", "start_date", "end_date", "status", "goals", "plan")
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "goals": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"


class ProgressEntryStaffForm(forms.ModelForm):
    class Meta:
        model = ProgressEntry
        fields = (
            "week_number",
            "title",
            "summary",
            "exercises_total",
            "exercises_completed",
            "clinician_notes",
            "recorded_at",
        )
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "clinician_notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "recorded_at": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"


class ConsultationStaffForm(forms.ModelForm):
    class Meta:
        model = ConsultationHistory
        fields = (
            "session_type",
            "session_date",
            "duration_minutes",
            "chief_complaint",
            "assessment_summary",
            "recommendations",
            "follow_up_required",
        )
        widgets = {
            "session_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "assessment_summary": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "recommendations": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
