from django.db.models import TextField, DateTimeField, ForeignKey, CASCADE, Model
from apps.tasks.models import Task
from apps.accounts.models import User


class Comment(Model):
    class Meta:
        ordering = ["created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    content: TextField = TextField(blank=False, null=False)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)
    task: ForeignKey = ForeignKey(Task, on_delete=CASCADE, related_name="comments")
    author: ForeignKey = ForeignKey(User, on_delete=CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.author.username} - {self.task.title}"

    def __repr__(self):
        return f"Comment(content={self.content}, task={self.task.title}, author={self.author.username})"
