import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import grades as grade_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.parametrize(
    ("username, password, expected_status"),
    [
        ("demo", "demo-password", 401),
        ("professor", "password", 200),
        ("professor", "wrong-password", 401),
        ("not professor", "password", 401),
    ],
)
def test_login(client: TestClient, username: str, password: str, expected_status: int):
    response = client.post("/", json={"username": username, "password": password})
    assert response.status_code == expected_status
    if expected_status == 401:
        assert response.json() == {"detail": "Invalid username or password."}


def test_save_grade_returns_and_persists_grade(
    client: TestClient, tmp_path, monkeypatch: pytest.MonkeyPatch
):
    grade_file = tmp_path / "grades.json"
    monkeypatch.setattr(grade_service, "GRADE_FILE", grade_file)

    response = client.post("/settings/grade", json={"name": "demo", "grade": "90"})

    assert response.status_code == 200
    assert response.json() == [{"name": "demo", "grade": "90"}]
    assert json.loads(grade_file.read_text(encoding="utf-8")) == response.json()


def test_save_grade_conflict_returns_409(
    client: TestClient, tmp_path, monkeypatch: pytest.MonkeyPatch
):
    grade_file = tmp_path / "grades.json"
    monkeypatch.setattr(grade_service, "GRADE_FILE", grade_file)

    client.post("/settings/grade", json={"name": "demo", "grade": "90"})

    # Attempt to save the same grade again
    response = client.post("/settings/grade", json={"name": "demo", "grade": "95"})

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "A grade for demo already exists. Use PATCH or PUT to change it."
    )

def test_patch_grade_updates_existing_grade(
    client: TestClient, tmp_path, monkeypatch: pytest.MonkeyPatch
):
    grade_file = tmp_path / "grades.json"
    monkeypatch.setattr(grade_service, "GRADE_FILE", grade_file)

    client.post("/settings/grade", json={"name": "demo", "grade": "90"})

    # Update the existing grade
    response = client.patch("/settings/grade", json={"name": "demo", "grade": "95"})

    assert response.status_code == 200
    assert response.json() == [{"name": "demo", "grade": "95"}]
    assert json.loads(grade_file.read_text(encoding="utf-8")) == response.json()

def test_patch_grade_updates_non_existing_grade(
    client: TestClient, tmp_path, monkeypatch: pytest.MonkeyPatch
):
    grade_file = tmp_path / "grades.json"
    monkeypatch.setattr(grade_service, "GRADE_FILE", grade_file)

    client.post("/settings/grade", json={"name": "demo", "grade": "90"})

    # Try to update a grade that does not exist
    response = client.patch("/settings/grade", json={"name": "demo4", "grade": "95"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Grade for demo4 not found."}
    assert json.loads(grade_file.read_text(encoding="utf-8")) == [
        {"name": "demo", "grade": "90"}
    ]

def test_put_grade_updates_existing_grade(
    client: TestClient, tmp_path, monkeypatch: pytest.MonkeyPatch
):
    grade_file = tmp_path / "grades.json"
    monkeypatch.setattr(grade_service, "GRADE_FILE", grade_file)

    client.post("/settings/grade", json={"name": "demo", "grade": "90"})

    # Update the existing grade using PUT
    response = client.put("/settings/grade", json={"name": "demo", "grade": "95"})

    assert response.status_code == 200
    assert response.json() == [{"name": "demo", "grade": "95"}]
    assert json.loads(grade_file.read_text(encoding="utf-8")) == response.json()


def test_put_non_existing_grade_creates_new_grade(
    client: TestClient, tmp_path, monkeypatch: pytest.MonkeyPatch
):
    grade_file = tmp_path / "grades.json"
    monkeypatch.setattr(grade_service, "GRADE_FILE", grade_file)

    client.post("/settings/grade", json={"name": "demo", "grade": "90"})

    # Update the existing grade using PUT
    response = client.put("/settings/grade", json={"name": "demo4", "grade": "95"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Grade for demo4 not found."}
    assert json.loads(grade_file.read_text(encoding="utf-8")) == [
        {"name": "demo", "grade": "90"}
    ]


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

def test_home_page_returns_html(client: TestClient):
    response = client.get("/home")
    html = " ".join(response.text.split())

    assert response.status_code == 200
    assert '<form id="grade-form">' in html
    assert '<label for="name">Name</label>' in html
    assert '<label for="grade">Grade</label>' in html
    assert '<button type="submit" name="method" value="POST">Add</button>' in html
    assert 'value="PATCH">Alter grade (PATCH)</button>' in html
    assert 'value="PUT">Replace grade (PUT)</button>' in html

def test_return_all_grades(client: TestClient,
                            tmp_path, monkeypatch: pytest.MonkeyPatch):
    grade_file = tmp_path / "grades.json"
    monkeypatch.setattr(grade_service, "GRADE_FILE", grade_file)

    # Add grades
    client.post("/settings/grade", json={"name": "demo1", "grade": "90"})
    client.post("/settings/grade", json={"name": "demo2", "grade": "85"})

    # Retrieve all grades
    response = client.get("/settings/grade")

    assert response.status_code == 200
    assert response.json() == [
        {"name": "demo1", "grade": "90"},
        {"name": "demo2", "grade": "85"},
    ]

def test_return_specific_grade(client: TestClient,
                               tmp_path, monkeypatch: pytest.MonkeyPatch):
    grade_file = tmp_path / "grades.json"
    monkeypatch.setattr(grade_service, "GRADE_FILE", grade_file)

    # Add grades
    client.post("/settings/grade", json={"name": "demo1", "grade": "90"})
    client.post("/settings/grade", json={"name": "demo2", "grade": "85"})

    # Retrieve specific grade
    response = client.get("/settings/grade/demo1")

    assert response.status_code == 200
    assert response.json() == {"name": "demo1", "grade": "90"}

def test_fail_to_return_specific_grade(client: TestClient,
                                       tmp_path, monkeypatch: pytest.MonkeyPatch):
    grade_file = tmp_path / "grades.json"
    monkeypatch.setattr(grade_service, "GRADE_FILE", grade_file)

    # Add grades
    client.post("/settings/grade", json={"name": "demo1", "grade": "90"})
    client.post("/settings/grade", json={"name": "demo2", "grade": "85"})

    # Retrieve specific grade
    response = client.get("/settings/grade/demo3")

    assert response.status_code == 404
    assert response.json() == {"detail": "Grade for demo3 not found."}

def test_delete_grades(client: TestClient, tmp_path, monkeypatch: pytest.MonkeyPatch):
    grade_file = tmp_path / "grades.json"
    monkeypatch.setattr(grade_service, "GRADE_FILE", grade_file)

    # Add grades
    client.post("/settings/grade", json={"name": "demo1", "grade": "90"})
    client.post("/settings/grade", json={"name": "demo2", "grade": "85"})

    # Delete all grades
    response = client.delete("/settings/grade")

    assert response.status_code == 200
    assert response.json() == {"message": "All grades deleted."}
    assert not grade_file.exists()

def test_invalid_endpoint_returns_404(client: TestClient):
    response = client.get("/invalid-endpoint")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
