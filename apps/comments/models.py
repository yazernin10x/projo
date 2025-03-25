from django.db.models import TextField, DateTimeField, ForeignKey, CASCADE, Model
from apps.tasks.models import Task
from apps.accounts.models import User


class Comment(Model):
    content: TextField = TextField()
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)
    task: ForeignKey = ForeignKey(Task, on_delete=CASCADE, related_name="comments")
    author: ForeignKey = ForeignKey(User, on_delete=CASCADE, related_name="comments")

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"

    def __repr__(self):
        return f"Comment(id={self.id}, content={self.content}, task={self.task.title}, author={self.author.username})"
