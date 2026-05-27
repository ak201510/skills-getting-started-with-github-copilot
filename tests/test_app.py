from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
INITIAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activity_data():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant():
    activity_name = quote("Chess Club")
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    activity_data = client.get("/activities").json()["Chess Club"]
    assert email in activity_data["participants"]


def test_duplicate_signup_returns_400():
    activity_name = quote("Chess Club")
    email = "michael@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    activity_name = quote("Chess Club")
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"

    activity_data = client.get("/activities").json()["Chess Club"]
    assert email not in activity_data["participants"]


def test_remove_missing_participant_returns_404():
    activity_name = quote("Chess Club")
    email = "missing@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
