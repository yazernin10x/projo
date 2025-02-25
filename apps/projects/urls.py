from django.urls import path
from .views import (
    ProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    add_members,
    remove_member,
)

app_name = "projects"

urlpatterns = [
    path("", ProjectListView.as_view(), name="list"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="detail"),
    path("create/", ProjectCreateView.as_view(), name="create"),
    path("<int:pk>/update/", ProjectUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ProjectDeleteView.as_view(), name="delete"),
    path("<int:pk>/add-members/", add_members, name="add_members"),
    path(
        "<int:pk>/remove-members/<int:member_id>/", remove_member, name="remove_members"
    ),
]
