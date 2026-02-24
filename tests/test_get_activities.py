"""
Tests for GET /activities endpoint
"""


def test_get_activities_returns_200(client):
    """Test that GET /activities returns 200 status code"""
    response = client.get("/activities")
    
    assert response.status_code == 200


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all 9 activities"""
    response = client.get("/activities")
    activities = response.json()
    
    assert len(activities) == 9
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    assert "Soccer Team" in activities
    assert "Basketball Club" in activities
    assert "Art Workshop" in activities
    assert "Drama Club" in activities
    assert "Math Olympiad" in activities
    assert "Science Club" in activities


def test_get_activities_has_correct_structure(client):
    """Test that each activity has required fields"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)


def test_get_activities_initial_participant_counts(client):
    """Test that activities have correct initial participant counts"""
    response = client.get("/activities")
    activities = response.json()
    
    # Each activity should start with 2 participants
    assert len(activities["Chess Club"]["participants"]) == 2
    assert len(activities["Programming Class"]["participants"]) == 2
    assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]


def test_get_activities_max_participants_values(client):
    """Test that max_participants are set correctly"""
    response = client.get("/activities")
    activities = response.json()
    
    assert activities["Chess Club"]["max_participants"] == 12
    assert activities["Programming Class"]["max_participants"] == 20
    assert activities["Gym Class"]["max_participants"] == 30
    assert activities["Math Olympiad"]["max_participants"] == 10
