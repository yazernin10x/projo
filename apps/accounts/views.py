from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView

from .forms import UserRegisterForm, UserUpdateForm
from .models import User

from http import HTTPStatus


class ProjoLoginView(LoginView):
    template_name = "accounts/login.html"
    success_message = "Connexion réussie ! Bienvenue"

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ProjoLogoutView(LogoutView):
    template_name = "accounts/logout.html"
    success_message = "Déconnexion réussie ! A bientôt"

    def dispatch(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().dispatch(request, *args, **kwargs)


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your account has been created successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Your form contains errors")
        response = super().form_invalid(form)
        response.status_code = HTTPStatus.UNPROCESSABLE_ENTITY
        return response


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserUpdateForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Your profile contains errors")
        response = super().form_invalid(form)
        response.status_code = HTTPStatus.UNPROCESSABLE_ENTITY
        return response


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/user_confirm_delete.html"
    success_url = reverse_lazy("index")
    context_object_name = "user"
    success_message = "Your account has been deleted successfully!"
