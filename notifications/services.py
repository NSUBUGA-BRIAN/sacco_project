from .models import Notification


def create_notification(user, message, notification_type='general', related_loan_id=None):
    """Create a notification for a user."""
    return Notification.objects.create(
        recipient=user,
        message=message,
        notification_type=notification_type,
        related_loan_id=related_loan_id
    )
