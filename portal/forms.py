from django import forms

from .models import Payment, ProgressEntry


class PaymentSubmissionForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = (
            "plan_label",
            "amount_inr",
            "upi_transaction_id",
            "payment_note",
            "screenshot",
        )
        widgets = {
            "plan_label": forms.TextInput(attrs={"readonly": "readonly"}),
            "payment_note": forms.TextInput(
                attrs={"placeholder": "Your name as shown in UPI payment"}
            ),
            "upi_transaction_id": forms.TextInput(
                attrs={"placeholder": "Optional UPI reference / transaction ID"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class GuestPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = (
            "guest_name",
            "guest_email",
            "guest_phone",
            "plan_label",
            "amount_inr",
            "upi_transaction_id",
            "payment_note",
            "screenshot",
        )
        labels = {
            "guest_name": "Full name",
            "guest_email": "Email",
            "guest_phone": "WhatsApp number",
        }
        widgets = {
            "plan_label": forms.TextInput(attrs={"readonly": "readonly"}),
            "guest_email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "guest_phone": forms.TextInput(attrs={"placeholder": "10-digit WhatsApp number"}),
            "payment_note": forms.TextInput(
                attrs={"placeholder": "Your name as shown in UPI payment"}
            ),
            "upi_transaction_id": forms.TextInput(
                attrs={"placeholder": "Optional UPI reference / transaction ID"}
            ),
        }

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
