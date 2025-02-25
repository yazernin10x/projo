from http import HTTPStatus
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Comment, Task
from .forms import CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, UpdateView, DeleteView


class CommentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Comment
    form_class = CommentForm
    success_message = "The comment has been successfully created."

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.task = get_object_or_404(Task, id=self.kwargs.get("task_pk"))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.task.pk})

    def form_invalid(self, form):
        message = "The form contains errors. Please correct the marked fields."
        messages.error(self.request, message)
        return self.render_to_response(
            self.get_context_data(form=form), status=HTTPStatus.UNPROCESSABLE_ENTITY
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = get_object_or_404(Task, id=self.kwargs.get("task_pk"))
        return context


class CommentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "comments/comment_form.html"
    context_object_name = "comment"
    success_message = "The comment has been successfully updated."

    def get_object(self):
        return get_object_or_404(Comment, id=self.kwargs.get("pk"))

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        message = "The form contains errors. Please correct the marked fields."
        messages.error(self.request, message)
        return self.render_to_response(
            self.get_context_data(form=form), status=HTTPStatus.UNPROCESSABLE_ENTITY
        )

    def get_success_url(self):
        if self.object.task.author == self.request.user:
            return reverse_lazy(
                "tasks:detail",
                kwargs={"pk": self.object.task.id},
            )
        else:
            return reverse_lazy(
                "tasks:detail-by-owner",
                kwargs={
                    "pk": self.object.task.id,
                    "owner_pk": self.object.task.author.id,
                },
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = get_object_or_404(Task, pk=self.object.task.pk)
        return context


class CommentDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Comment
    success_message = "The comment has been successfully deleted."

    def get_success_url(self):
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.task.id})
