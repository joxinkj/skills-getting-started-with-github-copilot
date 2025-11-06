import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_activity():
    return {
        "description": "Test activity for unit tests",
        "schedule": "Monday, 3:30 PM - 4:30 PM",
        "max_participants": 5,
        "participants": ["test1@mergington.edu", "test2@mergington.edu"]
    }

def test_root_redirect(client):
    """Test that root path redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    # Test at least one activity exists
    assert len(activities) > 0
    # Test activity structure
    first_activity = next(iter(activities.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity

def test_signup_success(client):
    """Test successful activity signup"""
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"

    # Verify student was added
    activities = client.get("/activities").json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_duplicate(client):
    """Test signing up a student who is already registered"""
    # First signup
    client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
    
    # Try to signup again
    response = client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up"

def test_signup_nonexistent_activity(client):
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=student@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_unregister_success(client):
    """Test successful activity unregistration"""
    # First sign up a student
    email = "todelete@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Then unregister them
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from Chess Club"

    # Verify student was removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]

def test_unregister_not_registered(client):
    """Test unregistering a student who is not registered"""
    response = client.delete("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student not registered for this activity"

def test_unregister_nonexistent_activity(client):
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/NonexistentClub/unregister?email=student@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"