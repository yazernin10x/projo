from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Comment, Task
from .forms import CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, UpdateView, DeleteView


class CommentCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "comments/comment_form_modal.html"
    success_message = "Le commentaire a été créé avec succès."

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.task = get_object_or_404(Task, pk=self.kwargs.get("task_pk"))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.task.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = get_object_or_404(Task, pk=self.kwargs.get("task_pk"))
        return context


class CommentUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "comments/comment_form_modal.html"
    context_object_name = "comment"
    success_message = "Le commentaire a été modifié avec succès."

    def get_success_url(self):
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.task.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = get_object_or_404(Task, pk=self.object.task.pk)
        return context


class CommentDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    success_message = "Le commentaire a été supprimé avec succès."

    def get_success_url(self):
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.task.pk})
