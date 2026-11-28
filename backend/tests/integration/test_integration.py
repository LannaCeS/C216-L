import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


# Home tests


def test_list_starts_empty(client):
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_book(client):
    response = client.post(
        "/books/",
        json={"title": "Dom Casmurro", "author": "Machado de Assis", "rating": 5},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["title"] == "Dom Casmurro"
    assert body["rating"] == 5


def test_get_book_by_id(client):
    book_id = client.post(
        "/books/", json={"title": "O Cortiço", "author": "Aluisio Azevedo", "rating": 4}
    ).json()["id"]

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "O Cortiço"


def test_get_missing_book_returns_404(client):
    assert client.get("/books/999").status_code == 404


def test_patch_updates_sent_fields(client):
    book_id = client.post(
        "/books/",
        json={"title": "Dom Casmurro", "author": "Machado de Assis", "rating": 3},
    ).json()["id"]

    response = client.patch(f"/books/{book_id}", json={"rating": 5})
    assert response.status_code == 200
    assert response.json()["rating"] == 5
    assert response.json()["title"] == "Dom Casmurro"


def test_delete_book(client):
    book_id = client.post(
        "/books/",
        json={"title": "Dom Casmurro", "author": "Machado de Assis", "rating": 3},
    ).json()["id"]

    assert client.delete(f"/books/{book_id}").status_code == 204
    assert client.get(f"/books/{book_id}").status_code == 404


def test_delete_missing_book_returns_404(client):
    assert client.delete("/books/999").status_code == 404


# Login tests
@pytest.fixture
def credentials(monkeypatch):
    monkeypatch.setenv("SINGLE_USER_EMAIL", "user@example.com")
    monkeypatch.setenv("SINGLE_USER_PASSWORD", "secret123")


def test_login_success(client, credentials):
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    assert response.json() == {"authenticated": True}


def test_login_wrong_password(client, credentials):
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "errada"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_login_wrong_email(client, credentials):
    response = client.post(
        "/auth/login",
        json={"email": "outro@example.com", "password": "secret123"},
    )
    assert response.status_code == 401


def test_login_is_case_sensitive(client, credentials):
    response = client.post(
        "/auth/login",
        json={"email": "USER@example.com", "password": "secret123"},
    )
    assert response.status_code == 401


def test_login_missing_field_returns_422(client, credentials):
    response = client.post("/auth/login", json={"email": "user@example.com"})
    assert response.status_code == 422


def test_login_without_server_credentials_returns_500(client, monkeypatch):
    monkeypatch.delenv("SINGLE_USER_EMAIL", raising=False)
    monkeypatch.delenv("SINGLE_USER_PASSWORD", raising=False)

    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "secret123"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Credentials not configured on the server."


@pytest.mark.parametrize("email,password", [("", ""), ("user@example.com", "")])
def test_login_empty_values_are_rejected(client, credentials, email, password):
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 401
