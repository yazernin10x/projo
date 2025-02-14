import re

from django.contrib.auth.forms import UserCreationForm
from django.forms import (
    ModelForm,
    EmailField,
    CharField,
    PasswordInput,
)
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import User


class UserRegisterForm(UserCreationForm):
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    username = CharField(required=True)
    email = EmailField(required=True, validators=[validate_email])
    password1 = CharField(widget=PasswordInput, required=True)
    password2 = CharField(widget=PasswordInput, required=True)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        pattern = r"^\+?[1-9]\d{1,14}$"
        if phone_number and not re.match(pattern, str(phone_number)):
            raise ValidationError("Enter a valid phone number.")
        return phone_number

    def clean(self):
        data = super().clean()
        if data.get("password1") != data.get("password2"):
            raise ValidationError("The passwords do not match.")
        return data

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "profile_picture",
            "password1",
            "password2",
            "bio",
        ]


class UserUpdateForm(ModelForm):
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    username = CharField(required=True)
    email = EmailField(required=True, validators=[validate_email])

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "profile_picture",
            "bio",
        ]
