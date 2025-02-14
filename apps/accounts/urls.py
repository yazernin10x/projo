from django.urls import path
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from .views import register, profile, UserDeleteView

app_name = "accounts"

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("register/", register, name="register"),
    path("delete/", UserDeleteView.as_view(), name="delete_account"),
    path(
        "login/", LoginView.as_view(template_name="accounts/login.html"), name="login"
    ),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
]

urlpatterns += [
    path(
        "password_change/",
        PasswordChangeView.as_view(template_name="accounts/password_change_form.html"),
        name="password_change",
    ),
    path(
        "password_change/done/",
        PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html"
        ),
        name="password_change_done",
    ),
]

urlpatterns += [
    path(
        "password_reset/",
        PasswordResetView.as_view(template_name="accounts/password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
