from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list_view(request):
    notifications = request.user.notifications.all()
    # Mark all as read
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def mark_read_view(request, pk):
    notif = request.user.notifications.filter(pk=pk).first()
    if notif:
        notif.is_read = True
        notif.save()
    return redirect('notifications:list')
