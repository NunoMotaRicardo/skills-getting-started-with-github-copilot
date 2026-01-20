import copy
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure src is on path for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from app import activities, app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_data():
    """Reset in-memory activity data between tests."""
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(snapshot))


def test_get_activities_lists_default_data():
    client = TestClient(app)
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Basketball" in data
    assert isinstance(data["Basketball"]["participants"], list)


def test_signup_adds_participant_and_updates_list():
    client = TestClient(app)
    activity = "Basketball"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_prevents_duplicates():
    client = TestClient(app)
    activity = "Basketball"
    email = "dupstudent@mergington.edu"

    first = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert first.status_code == 200

    duplicate = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert duplicate.status_code == 400
    assert "already" in duplicate.json()["detail"].lower()


def test_remove_participant_unregisters_student():
    client = TestClient(app)
    activity = "Soccer"
    existing_email = activities[activity]["participants"][0]

    response = client.delete(
        f"/activities/{activity}/participants", params={"email": existing_email}
    )
    assert response.status_code == 200
    assert existing_email not in activities[activity]["participants"]
