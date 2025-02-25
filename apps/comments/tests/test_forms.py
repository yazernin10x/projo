import pytest
from django.core.exceptions import ValidationError
from ..forms import CommentForm


class TestCommentForm:
    def test_comment_form_validation(self):
        form = CommentForm(data={"content": "This is a test comment."})
        assert form.is_valid()

    def test_comment_form_errors(self):
        with pytest.raises(ValidationError):
            form = CommentForm(data={"content": ""})
            form.full_clean()
            assert "content" in form.errors
            assert form.errors["content"] == ["The comment content is required."]

    def test_comment_form_widget_attrs(self):
        form = CommentForm()
        widget = form.fields["content"].widget.attrs
        assert widget.get("placeholder") == "Write a comment..."
        assert widget.get("rows") == 3
