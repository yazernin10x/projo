from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from .forms import UserRegisterForm, UserUpdateForm
from .models import User


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created successfully!")
            return redirect("index")
    else:
        form = UserRegisterForm()
    return render(request, "accouns/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("accounts:profile")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/user_confirm_delete.html"
    success_url = reverse_lazy("index")
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user
