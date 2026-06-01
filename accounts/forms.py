from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import PatientProfile, User


class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True, label="Full name")
    phone = forms.CharField(max_length=15, required=True, label="WhatsApp number")
    primary_concern = forms.CharField(
        max_length=120,
        required=False,
        label="Primary concern",
        widget=forms.TextInput(attrs={"placeholder": "e.g. ACL rehab, lower back pain"}),
    )

    class Meta:
        model = User
        fields = ("first_name", "email", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        user.whatsapp = self.cleaned_data["phone"]
        user.role = User.Role.PATIENT
        name = self.cleaned_data["first_name"].strip()
        parts = name.split(None, 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ""
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                primary_concern=self.cleaned_data.get("primary_concern", ""),
            )
        return user


class PatientLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"
        self.fields["username"].widget.attrs.update(
            {"placeholder": "you@example.com", "class": "form-control"}
        )
        self.fields["password"].widget.attrs.update({"class": "form-control"})


class PatientProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, label="Full name")
    phone = forms.CharField(max_length=15, required=True, label="WhatsApp number")
    email = forms.EmailField(required=True)

    class Meta:
        model = PatientProfile
        fields = (
            "primary_concern",
            "injury_history",
            "date_of_birth",
            "emergency_contact_name",
            "emergency_contact_phone",
        )
        widgets = {
            "injury_history": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.user.get_full_name()
        self.fields["phone"].initial = self.user.phone
        self.fields["email"].initial = self.user.email
        for field in self.fields.values():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data["first_name"].split()[0]
        rest = self.cleaned_data["first_name"].split()[1:]
        self.user.last_name = " ".join(rest)
        self.user.phone = self.cleaned_data["phone"]
        self.user.whatsapp = self.cleaned_data["phone"]
        self.user.email = self.cleaned_data["email"]
        self.user.save()
        if commit:
            profile.save()
        return profile
