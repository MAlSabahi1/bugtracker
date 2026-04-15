from django.conf import settings
from django.utils import translation
from core.models import Notification


def my_setting(request):
    return {"MY_SETTING": settings}


def environment(request):
    return {"ENVIRONMENT": getattr(settings, "ENVIRONMENT", "local")}


def language_direction(request):
    """
    Returns the current language and text direction (rtl/ltr) to templates.
    """
    return {
        "text_direction_value": "rtl" if translation.get_language() == "ar" else "ltr",
        "current_language": translation.get_language(),
    }


def notifications(request):
    """
    Returns unread notifications count and recent notifications for the logged-in user.
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        recent = Notification.objects.filter(recipient=request.user).order_by("-created_at")[:5]
        return {
            "unread_notifications_count": unread_count,
            "recent_notifications": recent,
        }
    return {}
