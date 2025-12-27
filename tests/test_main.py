# tests/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Portfolio" in response.text

def test_contact_form():
    response = client.post("/contact", data={
        "name": "Test User",
        "email": "test@example.com",
        "message": "Test message"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"