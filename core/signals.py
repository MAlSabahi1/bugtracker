from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Issue, Notification, User


@receiver(post_save, sender=Issue)
def create_issue_notifications(sender, instance, created, **kwargs):
    """
    Creates notifications for relevant team members and admins when a new issue is reported.
    """
    if created:
        # Determine notification message
        message = _("New issue reported: %(title)s") % {"title": instance.title}

        # Identify eligible recipients:
        # 1. Users with the role matching target_team
        # 2. All Admin users
        recipients = User.objects.filter(
            Q(role=instance.target_team) |
            Q(role=User.Role.ADMIN) |
            Q(is_superuser=True)
        ).distinct()

        # Create notifications (excluding the reporter if they are in the recipient list)
        notifications = []
        for recipient in recipients:
            if recipient != instance.reported_by:
                notifications.append(
                    Notification(
                        recipient=recipient,
                        issue=instance,
                        message=message
                    )
                )
        
        if notifications:
            Notification.objects.bulk_create(notifications)
