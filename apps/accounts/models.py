from django.db.models import (
    TextField,
    ImageField,
    DateTimeField,
    EmailField,
    CharField,
)
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from phonenumber_field.modelfields import PhoneNumberField


def validate_unique_email(value):
    """Check if the email is unique"""
    if User.objects.filter(email=value).exists():
        raise ValidationError("Email is already in use.")


def validate_unique_username(value):
    if User.objects.filter(username=value).exists():
        raise ValidationError("Username is already in use.")


class User(AbstractUser):
    class Meta:
        ordering = ["username"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    username: CharField = CharField(
        max_length=30,
        unique=True,
        validators=[validate_unique_username],
        error_messages={"unique": "This username is already in use."},
    )
    email: EmailField = EmailField(
        unique=True,
        validators=[validate_unique_email],
        error_messages={"unique": "This email is already in use."},
    )
    profile_picture: ImageField = ImageField(
        upload_to="profiles/", blank=True, null=True
    )
    phone_number: PhoneNumberField = PhoneNumberField(blank=True, null=True)
    bio: TextField = TextField(blank=True, null=True)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.username == "admin":
            raise ValidationError("The username 'admin' is reserved.")

    def save(self, *args, **kwargs):
        # validate_unique_email(self.email)
        # validate_unique_username(self.username)
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.email}"

    def __repr__(self) -> str:
        return f"User(username='{self.username}', email='{self.email}')"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
