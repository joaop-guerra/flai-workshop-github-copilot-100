"""
Tests for DELETE /activities/{activity_name}/participants/{email} endpoint
"""
from urllib.parse import quote


def test_remove_participant_success(client):
    """Test successfully removing a participant from an activity"""
    # michael@mergington.edu is initially in Chess Club
    response = client.delete(
        "/activities/Chess%20Club/participants/michael@mergington.edu"
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert len(activities["Chess Club"]["participants"]) == 1


def test_remove_participant_decreases_count(client):
    """Test that removing participant decreases participant count"""
    # Get initial count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()["Programming Class"]["participants"])
    
    # Remove a participant
    client.delete(
        "/activities/Programming%20Class/participants/emma@mergington.edu"
    )
    
    # Verify count decreased
    final_response = client.get("/activities")
    final_count = len(final_response.json()["Programming Class"]["participants"])
    assert final_count == initial_count - 1


def test_remove_participant_nonexistent_activity_returns_404(client):
    """Test that removing from non-existent activity returns 404"""
    response = client.delete(
        "/activities/Nonexistent%20Activity/participants/test@mergington.edu"
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_not_in_activity_returns_404(client):
    """Test that removing a participant not in the activity returns 404"""
    response = client.delete(
        "/activities/Chess%20Club/participants/notamember@mergington.edu"
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_remove_last_participant(client):
    """Test removing participants until activity is empty"""
    # Remove both participants from Chess Club
    response1 = client.delete(
        "/activities/Chess%20Club/participants/michael@mergington.edu"
    )
    assert response1.status_code == 200
    
    response2 = client.delete(
        "/activities/Chess%20Club/participants/daniel@mergington.edu"
    )
    assert response2.status_code == 200
    
    # Verify activity has no participants
    activities = client.get("/activities").json()
    assert len(activities["Chess Club"]["participants"]) == 0


def test_remove_then_signup_again(client):
    """Test that a removed participant can sign up again"""
    email = "michael@mergington.edu"
    
    # Remove participant
    response1 = client.delete(f"/activities/Chess%20Club/participants/{email}")
    assert response1.status_code == 200
    
    # Sign up again
    response2 = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response2.status_code == 200
    
    # Verify participant is back
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_remove_from_full_activity_allows_new_signup(client):
    """Test that removing from a full activity opens up a spot"""
    # Fill Math Olympiad to capacity (max 10, starts with 2)
    for i in range(8):
        client.post(f"/activities/Math%20Olympiad/signup?email=student{i}@mergington.edu")
    
    # Verify it's full
    response = client.post(
        "/activities/Math%20Olympiad/signup?email=overflow@mergington.edu"
    )
    assert response.status_code == 400
    
    # Remove one participant
    client.delete(
        "/activities/Math%20Olympiad/participants/william@mergington.edu"
    )
    
    # Now signup should work
    response = client.post(
        "/activities/Math%20Olympiad/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200


def test_remove_with_url_encoded_names(client):
    """Test remove works with URL encoded activity names and emails"""
    response = client.delete(
        f"/activities/{quote('Drama Club')}/participants/{quote('ella@mergington.edu')}"
    )
    
    assert response.status_code == 200
    assert "Drama Club" in response.json()["message"]


def test_remove_participant_from_multiple_activities(client):
    """Test removing the same email from different activities"""
    email = "test@mergington.edu"
    
    # Sign up for two activities
    client.post(f"/activities/Chess%20Club/signup?email={email}")
    client.post(f"/activities/Drama%20Club/signup?email={email}")
    
    # Remove from Chess Club
    response1 = client.delete(f"/activities/Chess%20Club/participants/{email}")
    assert response1.status_code == 200
    
    # Should still be in Drama Club
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]
    assert email in activities["Drama Club"]["participants"]
    
    # Remove from Drama Club too
    response2 = client.delete(f"/activities/Drama%20Club/participants/{email}")
    assert response2.status_code == 200
    
    # Should be in neither
    activities = client.get("/activities").json()
    assert email not in activities["Drama Club"]["participants"]


def test_remove_participant_twice_returns_404(client):
    """Test that removing the same participant twice returns 404"""
    email = "michael@mergington.edu"
    
    # Remove once - should succeed
    response1 = client.delete(f"/activities/Chess%20Club/participants/{email}")
    assert response1.status_code == 200
    
    # Remove again - should fail
    response2 = client.delete(f"/activities/Chess%20Club/participants/{email}")
    assert response2.status_code == 404
    assert response2.json()["detail"] == "Participant not found in this activity"
