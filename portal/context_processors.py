from .models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        try:
            student = request.user.studentprofile
            notifications = Notification.objects.filter(student=student).order_by('-created_at')
            unread_notifications = notifications.filter(is_read=False)
            return {
                'notifications': notifications,
                'unread_notifications': unread_notifications,
            }
        except:
            # handle cases like superuser without StudentProfile
            return {}
    return {}