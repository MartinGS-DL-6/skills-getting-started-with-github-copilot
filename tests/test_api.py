import copy
import pytest
from fastapi.testclient import TestClient
import src.app as app_module

@pytest.fixture(autouse=True)
def activities_backup():
    # Arrange: snapshot the in-memory activities and restore after each test
    backup = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(backup)

@pytest.fixture
def client():
    with TestClient(app_module.app) as c:
        yield c


def test_get_activities(client):
    # Arrange: none
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_prevent_duplicate(client):
    # Arrange
    activity = "Chess Club"
    email = "testuser@example.com"

    # Act: sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Act: duplicate signup
    resp_dup = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert duplicate rejected
    assert resp_dup.status_code == 400


def test_remove_participant(client):
    # Arrange
    activity = "Chess Club"
    existing = app_module.activities[activity]["participants"][0]

    # Act
    resp = client.delete(f"/activities/{activity}/signup", params={"email": existing})
    # Assert
    assert resp.status_code == 200
    assert existing not in app_module.activities[activity]["participants"]


def test_remove_nonexistent_returns_404(client):
    # Arrange
    activity = "Chess Club"
    nonmember = "ghost@example.com"

    # Act
    resp = client.delete(f"/activities/{activity}/signup", params={"email": nonmember})
    # Assert
    assert resp.status_code == 404
