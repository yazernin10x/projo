import pytest
from ..models import Comment


class TestCommentModel:
    @pytest.mark.django_db(transaction=True)
    def test_creation(self, comment: Comment):
        assert comment.content == "Test comment"
        assert comment.task.title == "Test Task"
        assert comment.author.username == "john.doe"

    @pytest.mark.django_db(transaction=True)
    def test__str__(self, comment: Comment):
        username = comment.author.username
        task_title = comment.task.title
        expected_str = f"Comment by {username} on {task_title}"
        assert str(comment) == expected_str

    @pytest.mark.django_db(transaction=True)
    def test__repr__(self, comment: Comment):
        id = comment.id
        content = comment.content
        task = comment.task.title
        author = comment.author.username
        expected_repr = (
            f"Comment(id={id}, content={content}, task={task}, author={author})"
        )
        assert repr(comment) == expected_repr

    @pytest.mark.django_db(transaction=True)
    def test_auto_timestamps(self, comment: Comment):
        assert comment.created_at is not None
        assert comment.updated_at is not None
