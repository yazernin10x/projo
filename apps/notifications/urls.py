from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="list"),
    path("<int:pk>/mark-as-read/", views.mark_as_read, name="mark_as_read"),
    path("<int:pk>/mark-as-unread/", views.mark_as_unread, name="mark_as_unread"),
    path("mark-all-as-read/", views.mark_all_as_read, name="mark_all_as_read"),
    path("mark-all-as-unread/", views.mark_all_as_unread, name="mark_all_as_unread"),
    path("<int:pk>/delete/", views.DeleteNotificationView.as_view(), name="delete"),
    path("delete-all/", views.delete_all_notifications, name="delete_all"),
]
