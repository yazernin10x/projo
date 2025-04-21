from datetime import timedelta

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = 12
    paginate_orphans = 2

    def get_queryset(self):
        queryset = Notification.objects.filter(recipients=self.request.user)

        # Application des filtres
        status = self.request.GET.get("status")
        sender = self.request.GET.get("sender")
        date_filter = self.request.GET.get("date")

        if status == "unread":
            queryset = queryset.filter(is_read=False)
        elif status == "read":
            queryset = queryset.filter(is_read=True)

        if sender:
            queryset = queryset.filter(sender__username=sender)

        if date_filter == "today":
            queryset = queryset.filter(created_at__date=timezone.now().date())
        elif date_filter == "this_week":
            start_week = timezone.now().date() - timedelta(
                days=timezone.now().weekday()
            )
            queryset = queryset.filter(created_at__date__gte=start_week)
        elif date_filter == "this_month":
            queryset = queryset.filter(created_at__month=timezone.now().month)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Liste des expéditeurs distincts pour le filtre
        context["senders"] = (
            Notification.objects.filter(recipients=self.request.user)
            .values_list("sender__username", flat=True)
            .distinct()
        )
        queryset = self.get_queryset()
        context["unread_notifications"] = queryset.filter(is_read=False)
        context["read_notifications"] = queryset.filter(is_read=True)
        return context


@require_POST
@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipients=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, "Notification marquée comme lue")
    return redirect("notifications:list")


@require_POST
@login_required
def mark_all_as_read(request):
    query = Notification.objects.filter(is_read=False)
    nb_notifications = query.update(is_read=True)
    if nb_notifications > 0:
        messages.success(
            request, "Toutes les notifications ont été marquées comme lues"
        )
    else:
        messages.info(request, "Aucune notification à marquer comme lue")
    return redirect("notifications:list")


@require_POST
@login_required
def mark_as_unread(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipients=request.user)
    notification.is_read = False
    notification.save()
    messages.success(request, "Notification marquée comme non lue")
    return redirect("notifications:list")


@require_POST
@login_required
def mark_all_as_unread(request):
    query = Notification.objects.filter(is_read=True)
    nb_notifications = query.update(is_read=False)
    if nb_notifications > 0:
        messages.success(
            request, "Toutes les notifications ont été marquées comme non lues"
        )
    else:
        messages.info(request, "Aucune notification à marquer comme non lue")
    return redirect("notifications:list")


class DeleteNotificationView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Notification
    success_url = reverse_lazy("notifications:list")
    success_message = "Notification supprimée avec succès"


@require_POST
@login_required
def delete_all_notifications(request):
    Notification.objects.filter(
        Q(recipients=request.user) | Q(sender=request.user)
    ).delete()
    messages.success(request, "Toutes les notifications ont été supprimées")
    return redirect("notifications:list")
