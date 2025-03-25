import pytest

from ..models import User

FIRST_NAME = "John"
LAST_NAME = "Doe"
USERNAME = "john.doe"
PHONE_NUMBER = "+33666666666"
EMAIL = "john.doe@example.com"
PASSWORD = "zootoR587"


@pytest.fixture(scope="function")
def form_data():
    return {
        "first_name": FIRST_NAME,
        "last_name": LAST_NAME,
        "username": USERNAME,
        "phone_number": PHONE_NUMBER,
        "email": EMAIL,
    }


@pytest.fixture(scope="function")
def user():
    return User.objects.create_user(
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        username=USERNAME,
        phone_number=PHONE_NUMBER,
        email=EMAIL,
        password=PASSWORD,
    )
