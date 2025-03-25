from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("<int:pk>/", views.TaskDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", views.TaskUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.TaskDeleteView.as_view(), name="delete"),
    path(
        "project/<int:project_pk>/create/",
        views.TaskCreateView.as_view(),
        name="create",
    ),
    path(
        "<int:pk>/owner/<int:owner_pk>/detail",
        views.TaskDetailView.as_view(),
        name="detail-by-owner",
    ),
    path(
        "<int:task_pk>/comment-create-form/",
        views.get_comment_create_form,
        name="get_comment_create_form",
    ),
    path(
        "<int:comment_pk>/comment-update-form/",
        views.get_comment_update_form,
        name="get_comment_update_form",
    ),
]
