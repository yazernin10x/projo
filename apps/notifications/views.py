from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Notification

from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import DeleteView


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return Notification.objects.filter(
            Q(recipients=self.request.user) | Q(sender=self.request.user)
        ).order_by("-created_at")


@require_GET
@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipients=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, "Notification marked as read")
    return redirect("notifications:list")


@require_GET
@login_required
def mark_all_as_read(request):
    query = request.user.notifications.filter(is_read=False)
    nb_notifications = query.update(is_read=True)
    if nb_notifications > 0:
        messages.success(request, "All notifications marked as read")
    else:
        messages.info(request, "No notifications to mark as read")

    return redirect("notifications:list")


@require_GET
@login_required
def mark_as_unread(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipients=request.user)
    notification.is_read = False
    notification.save()
    messages.success(request, "Notification marquée comme non lue")
    return redirect("notifications:list")


@require_GET
@login_required
def mark_all_as_unread(request):
    query = request.user.notifications.filter(is_read=True)
    nb_notifications = query.update(is_read=False)
    if nb_notifications > 0:
        messages.success(
            request, "Toutes les notifications ont été marquées comme non lues"
        )
    else:
        messages.info(request, "Aucune notification à marquer comme non lue")

    return redirect("notifications:list")


class DeleteNotificationView(LoginRequiredMixin, DeleteView):
    model = Notification
    success_url = reverse_lazy("notifications:list")

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(Q(recipients=self.request.user) | Q(sender=self.request.user))
        )


@require_POST
@login_required
def delete_all_notifications(request):
    Notification.objects.filter(
        Q(recipients=request.user) | Q(sender=request.user)
    ).delete()
    messages.success(request, "Toutes les notifications ont été supprimées")
    return redirect("notifications:list")
