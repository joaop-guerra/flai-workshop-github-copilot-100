"""
Tests for POST /activities/{activity_name}/signup endpoint
"""
from urllib.parse import quote


def test_signup_new_student_success(client):
    """Test successfully signing up a new student"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    
    # Verify student was added
    activities = client.get("/activities").json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    assert len(activities["Chess Club"]["participants"]) == 3


def test_signup_increases_participant_count(client):
    """Test that signup increases participant count"""
    # Get initial count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()["Programming Class"]["participants"])
    
    # Sign up new student
    client.post("/activities/Programming%20Class/signup?email=test@mergington.edu")
    
    # Verify count increased
    final_response = client.get("/activities")
    final_count = len(final_response.json()["Programming Class"]["participants"])
    assert final_count == initial_count + 1


def test_signup_nonexistent_activity_returns_404(client):
    """Test that signing up for non-existent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student_returns_400(client):
    """Test that signing up a student already enrolled returns 400"""
    # michael@mergington.edu is already in Chess Club
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_full_activity_returns_400(client):
    """Test that signing up for a full activity returns 400"""
    # Math Olympiad has max_participants=10, currently has 2
    # Fill it up to capacity
    for i in range(8):
        response = client.post(
            f"/activities/Math%20Olympiad/signup?email=student{i}@mergington.edu"
        )
        assert response.status_code == 200
    
    # Now it should be full, next signup should fail
    response = client.post(
        "/activities/Math%20Olympiad/signup?email=overflow@mergington.edu"
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
    
    # Verify participant wasn't added
    activities = client.get("/activities").json()
    assert "overflow@mergington.edu" not in activities["Math Olympiad"]["participants"]
    assert len(activities["Math Olympiad"]["participants"]) == 10


def test_signup_exactly_at_capacity(client):
    """Test signing up the last available spot"""
    # Math Olympiad has max_participants=10, currently has 2
    # Fill up to 9 participants
    for i in range(7):
        client.post(f"/activities/Math%20Olympiad/signup?email=student{i}@mergington.edu")
    
    # Sign up the last spot
    response = client.post(
        "/activities/Math%20Olympiad/signup?email=laststudent@mergington.edu"
    )
    
    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert len(activities["Math Olympiad"]["participants"]) == 10
    assert "laststudent@mergington.edu" in activities["Math Olympiad"]["participants"]


def test_signup_with_url_encoded_activity_name(client):
    """Test signup works with URL encoded activity names"""
    response = client.post(
        f"/activities/{quote('Drama Club')}/signup?email=actor@mergington.edu"
    )
    
    assert response.status_code == 200
    assert "Drama Club" in response.json()["message"]


def test_signup_multiple_activities_same_student(client):
    """Test that a student can sign up for multiple different activities"""
    email = "versatile@mergington.edu"
    
    # Sign up for Chess Club
    response1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response1.status_code == 200
    
    # Sign up for Drama Club
    response2 = client.post(f"/activities/Drama%20Club/signup?email={email}")
    assert response2.status_code == 200
    
    # Verify student is in both activities
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]
    assert email in activities["Drama Club"]["participants"]
