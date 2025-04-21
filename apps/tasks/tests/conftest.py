import pytest
from apps.core.constants import TASK_TITLE, TASK_STATUS

from apps.core.tests.fixtures import (
    user_1,
    user_2,
    user_1_connected,
    user_2_connected,
    project,
    task,
    comment,
    superuser,
    moderator,
    project_with_moderator,
    unauthorized_user,
)


@pytest.fixture(scope="function")
def form_data():
    return {
        "title": TASK_TITLE,
        "status": TASK_STATUS,
    }
