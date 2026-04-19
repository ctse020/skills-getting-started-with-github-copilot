"""
FastAPI backend tests for the Mergington High School activity management system.
Uses AAA pattern (Arrange, Act, Assert) with fixtures to reset global state.
"""

from fastapi.testclient import TestClient
from urllib.parse import quote
import copy
import pytest
from src.app import app, activities


INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    # Arrange: Store initial state
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    
    yield
    
    # Cleanup: Reset state after test
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    """Create a TestClient for API testing."""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with 200 status."""
        # Arrange: n/a (using default fixture state)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["max_participants"] == 12


class TestSignupActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant_success(self, client):
        """Test that a new participant can sign up for an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_participant_returns_400(self, client):
        """Test that duplicate signup returns 400 error."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signup for nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with activity name containing special characters."""
        # Arrange
        activity_name = "Programming Class"
        email = "dev@mergington.edu"
        encoded_name = quote(activity_name)
        
        # Act
        response = client.post(
            f"/activities/{encoded_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_remove_existing_participant_success(self, client):
        """Test that an existing participant can be removed."""
        # Arrange
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]
        
        # Act
        response = client.delete(
            f"/activities/{quote(activity_name)}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
    
    def test_remove_missing_participant_returns_404(self, client):
        """Test that removing a missing participant returns 404."""
        # Arrange
        activity_name = "Chess Club"
        email = "missing@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{quote(activity_name)}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"