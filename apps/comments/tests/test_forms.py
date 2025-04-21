from apps.comments.forms import CommentForm
from apps.core.constants import COMMENT_CONTENT


class TestCommentForm:
    def test_form_valid(self):
        form = CommentForm(data={"content": COMMENT_CONTENT})
        assert form.is_valid()
        assert form.cleaned_data["content"] == COMMENT_CONTENT
        assert form.errors == {}

    def test_form_invalid(self):
        form = CommentForm(data={"content": ""})
        assert not form.is_valid()
        assert form.errors["content"] == ["Ce champ est obligatoire."]
