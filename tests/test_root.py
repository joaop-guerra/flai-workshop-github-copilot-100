"""
Tests for root endpoint (/)
"""


def test_root_redirects_to_static_index(client):
    """Test that root endpoint redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_root_redirect_follows_successfully(client):
    """Test that following the redirect works"""
    response = client.get("/", follow_redirects=True)
    
    # Should successfully load the static page
    assert response.status_code == 200
