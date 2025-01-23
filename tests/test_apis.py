import pytest


@pytest.mark.asyncio
async def test_create_notification(client):
    payload = {
        "user_id": 1,
        "title": "Test Notification",
        "content": "This is a test notification.",
    }
    response = client.post("/api/v1/notifications/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["title"] == "Test Notification"
    assert data["content"] == "This is a test notification."


@pytest.mark.asyncio
async def test_mark_notification_read(client):
    payload = {
        "user_id": 1,
        "title": "Test Notification",
        "content": "This is a test notification.",
    }
    create_response = client.post("/api/v1/notifications", json=payload)
    notification_id = create_response.json()["id"]

    mark_read_payload = {
        "user_id": 1,
        "notification_ids": [notification_id],
        "read": True,
    }
    mark_read_response = client.put(
        "/api/v1/notifications/mark-read", json=mark_read_payload
    )
    assert mark_read_response.status_code == 200
    assert mark_read_response.json()["detail"] == "1 notifications marked as read"
