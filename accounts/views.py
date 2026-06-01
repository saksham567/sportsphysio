from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from accounts.models import User

from .forms import PatientLoginForm, PatientProfileForm, PatientRegistrationForm


class PatientLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = PatientLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or user.role == User.Role.STAFF or user.is_staff:
            return reverse_lazy("staff:dashboard")
        return reverse_lazy("portal:dashboard")


def register(request):
    if request.user.is_authenticated:
        return redirect("portal:dashboard")
    if request.method == "POST":
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("portal:dashboard")
    else:
        form = PatientRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_edit(request):
    profile, _ = request.user.patient_profile.__class__.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = PatientProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("portal:dashboard")
    else:
        form = PatientProfileForm(instance=profile, user=request.user)
    return render(request, "accounts/profile_edit.html", {"form": form})


@require_POST
@login_required
def logout_view(request):
    logout(request)
    return redirect("website:home")
