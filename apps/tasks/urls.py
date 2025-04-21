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
    path("<int:pk>/update-status/", views.update_task_status, name="update_status"),
]
