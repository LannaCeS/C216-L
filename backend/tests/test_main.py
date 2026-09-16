import pytest
from fastapi.testclient import TestClient

from src.backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.parametrize(
    ("username, password, expected_status"),
    [
        ("demo", "demo-password", 200),
        ("not demo", "wrong-password", 401),
        ("demo", "wrong-password", 401),
        ("not demo", "demo-password", 401),
    ],
)
def test_login(client: TestClient, username: str, password: str, expected_status: int):
    response = client.post("/", json={"username": username, "password": password})
    assert response.status_code == expected_status
    if expected_status == 401:
        assert response.json() == {"detail": "Invalid username or password."}


def test_save_email_returns_username_and_email(client: TestClient):
    response = client.post("/settings/email", json={"email": "demo@example.com"})

    assert response.status_code == 200
    assert response.json() == {"username": "demo", "email": "demo@example.com"}


def test_logout_redirects_to_home(client: TestClient):
    response = client.post("/logout", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_login_page_returns_html(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200
    assert '<form id="login-form">' in response.text
    assert '<label for="username">Username</label>' in response.text
    assert '<label for="password">Password</label>' in response.text
    assert '<button type="submit">Login</button>' in response.text


def test_invalid_endpoint_returns_404(client: TestClient):
    response = client.get("/invalid-endpoint")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
