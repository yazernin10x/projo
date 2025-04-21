from http import HTTPStatus
from django.utils import timezone
from datetime import timedelta

# User Data
FIRST_NAME_1 = "John"
LAST_NAME_1 = "Doe"
USERNAME_1 = "john.doe"
PHONE_NUMBER_1 = "+33666666666"
EMAIL_1 = "john.doe@example.com"
PASSWORD_1 = "zootoR587"

FIRST_NAME_2 = "Jane"
LAST_NAME_2 = "Doe"
USERNAME_2 = "jane.doe"
PHONE_NUMBER_2 = "+33666666667"
EMAIL_2 = "jane.doe@example.com"
PASSWORD_2 = "zootoR586"

# Project Data
PROJECT_TITLE = "Test Project"
PROJECT_DESCRIPTION = "Project description"
PROJECT_MEMBER_ROLE = "moderator"
PROJECT_DEADLINE = timezone.now() + timedelta(days=10)

# Task Data
TASK_TITLE = "Test Task"
TASK_DESCRIPTION = "Task description"
TASK_STATUS = "todo"
TASK_DEADLINE = timezone.now() + timedelta(days=10)

# Comment Data
COMMENT_CONTENT = "Test comment"

# Notification Data
NOTIFICATION_TITLE = "Test notification"
NOTIFICATION_CONTENT = "Test notification content"

# HTTP Status Codes
HTTP_200_OK = HTTPStatus.OK
HTTP_302_REDIRECT = HTTPStatus.FOUND
HTTP_400_BAD_REQUEST = HTTPStatus.BAD_REQUEST
HTTP_403_FORBIDDEN = HTTPStatus.FORBIDDEN
HTTP_404_NOT_FOUND = HTTPStatus.NOT_FOUND
HTTP_405_METHOD_NOT_ALLOWED = HTTPStatus.METHOD_NOT_ALLOWED
HTTP_500_INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR
