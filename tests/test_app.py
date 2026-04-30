import copy

import pytest
from httpx import Client

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all_activities():
    with Client(app=app, base_url="http://testserver") as client:
        response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_adds_participant():
    with Client(app=app, base_url="http://testserver") as client:
        response = client.post(
            "/activities/Chess%20Club/signup?email=testuser@mergington.edu"
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up testuser@mergington.edu for Chess Club"
    assert "testuser@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    email = "michael@mergington.edu"
    with Client(app=app, base_url="http://testserver") as client:
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_participant():
    email = "daniel@mergington.edu"
    with Client(app=app, base_url="http://testserver") as client:
        response = client.delete(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered daniel@mergington.edu from Chess Club"
    assert email not in activities["Chess Club"]["participants"]
