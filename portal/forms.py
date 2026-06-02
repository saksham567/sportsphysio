from django import forms

from .models import Payment, ProgressEntry


class RazorpayCheckoutForm(forms.Form):
    guest_name = forms.CharField(max_length=200, label="Full name")
    guest_email = forms.EmailField(label="Email")
    guest_phone = forms.CharField(
        max_length=15,
        label="WhatsApp number",
        widget=forms.TextInput(attrs={"placeholder": "10-digit WhatsApp number"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ProgressNoteForm(forms.ModelForm):
    class Meta:
        model = ProgressEntry
        fields = ("pain_level", "patient_notes")
        widgets = {
            "patient_notes": forms.Textarea(attrs={"rows": 3, "placeholder": "How did this week feel?"}),
            "pain_level": forms.NumberInput(attrs={"min": 0, "max": 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
