from datetime import datetime

from app.models import Notification


def test_create_notification():
    notification = Notification(
        user_id=1,
        title="Test Notification",
        content="This is a test notification.",
        created_at=datetime.utcnow(),
        read_at=None,
    )
    assert notification.user_id == 1
    assert notification.title == "Test Notification"
    assert notification.content == "This is a test notification."
    assert notification.read_at is None
