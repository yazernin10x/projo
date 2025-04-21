from django.urls import path
from apps.projects import views

app_name = "projects"

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="list"),
    path("<int:pk>/", views.ProjectDetailView.as_view(), name="detail"),
    path("create/", views.ProjectCreateView.as_view(), name="create"),
    path("<int:pk>/update/", views.ProjectUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.ProjectDeleteView.as_view(), name="delete"),
    path("<int:pk>/update-status/", views.update_project_status, name="update_status"),
    path("<int:pk>/manage-members/", views.manage_members, name="manage_members"),
    path(
        "<int:pk>/remove-member/<int:member_pk>/",
        views.remove_member,
        name="remove_member",
    ),
]
