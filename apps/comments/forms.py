from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Comment


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if not content:
            raise ValidationError("The comment content is required.")
        return content
