from django.db.models import (
    DateTimeField,
    EmailField,
)
from django.contrib.auth.models import AbstractUser

from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    class Meta:
        ordering = ["first_name", "last_name", "username"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    email = EmailField("Adresse email", unique=True, blank=False, null=False)
    phone_number: PhoneNumberField = PhoneNumberField(blank=True, null=True)
    date_updated: DateTimeField = DateTimeField(auto_now=True)

    def __repr__(self) -> str:
        return f"User(username='{self.username}', email='{self.email}')"
