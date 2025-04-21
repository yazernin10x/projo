import pytest
from apps.comments.models import Comment
from apps.core.constants import COMMENT_CONTENT, TASK_TITLE, USERNAME_1


@pytest.mark.django_db(transaction=True)
class TestCommentModel:
    def test_creation(self, user_1_connected: User, comment: Comment):
        assert comment.content == COMMENT_CONTENT
        assert comment.task.title == TASK_TITLE
        assert comment.author.username == USERNAME_1

    def test__str__(self, comment: Comment):
        username = comment.author.username
        task_title = comment.task.title
        assert str(comment) == f"{username} - {task_title}"

    def test__repr__(self, user_1_connected: User, comment: Comment):
        content = comment.content
        task = comment.task.title
        author = comment.author.username
        assert (
            repr(comment) == f"Comment(content={content}, task={task}, author={author})"
        )
