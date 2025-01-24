import pytest


@pytest.mark.asyncio
async def test_create_notification(client):
    payload = {
        "user_id": 1,
        "title": "Test Notification",
        "content": "This is a test notification.",
    }
    response = client.post("/api/v1/notifications", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["title"] == "Test Notification"
    assert data["content"] == "This is a test notification."


@pytest.mark.asyncio
async def test_create_notification_missing_field(client):
    payload = {"title": "Test Notification"}
    response = client.post("/api/v1/notifications", json=payload)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_mark_notifications_read(client):
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
    response = client.put("/api/v1/notifications/mark-read", json=mark_read_payload)
    assert response.status_code == 200
    assert response.json()["detail"] == "1 notifications marked as read"


@pytest.mark.asyncio
async def test_mark_all_notifications_read(client):
    mark_read_payload = {"user_id": 1, "mark_all": True, "read": True}
    response = client.put("/api/v1/notifications/mark-read", json=mark_read_payload)
    assert response.status_code == 200
    assert "notifications marked as read" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_unread_count(client):
    response = client.get("/api/v1/notifications/unread/count?user_id=1")
    assert response.status_code == 200
    assert "unread_count" in response.json()
    assert isinstance(response.json()["unread_count"], int)


@pytest.mark.asyncio
async def test_list_notifications(client):
    payload = {
        "user_id": 1,
        "title": "Test Notification",
        "content": "This is a test notification.",
    }
    client.post("/api/v1/notifications", json=payload)

    response = client.get("/api/v1/notifications?user_id=1")
    assert response.status_code == 200
    data = response.json().get("data")
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_notifications_with_search(client):
    response = client.get("/api/v1/notifications?user_id=1&search_text=Test")
    assert response.status_code == 200
    data = response.json().get("data")
    assert isinstance(data, list)
    for notification in data:
        assert "Test" in notification["title"] or "Test" in notification["content"]
