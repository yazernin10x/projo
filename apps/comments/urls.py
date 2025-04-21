from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path("task/<int:task_pk>/create", views.CommentCreateView.as_view(), name="create"),
    path("<int:pk>/update", views.CommentUpdateView.as_view(), name="update"),
    path("<int:pk>/delete", views.CommentDeleteView.as_view(), name="delete"),
]
