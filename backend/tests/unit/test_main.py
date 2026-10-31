import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.item import Item
from app.services import import_grades


@pytest.fixture
def test_sessions():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    try:
        yield sessions
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(test_sessions):
    def override_get_db():
        with test_sessions() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("username", "password", "expected_status"),
    [
        ("demo", "demo-password", 401),
        ("professor", "password", 200),
        ("professor", "wrong-password", 401),
        ("not professor", "password", 401),
    ],
)
def test_login(client, username, password, expected_status):
    response = client.post("/", json={"username": username, "password": password})

    assert response.status_code == expected_status
    if expected_status == 401:
        assert response.json() == {"detail": "Invalid username or password."}


def test_create_numeric_grade_persists_in_database(client, test_sessions):
    response = client.post("/settings/grade", json={"name": "Ada", "grade": "90"})

    assert response.status_code == 200
    assert response.json() == [{"name": "Ada", "grade": 90.0}]
    with test_sessions() as db:
        saved_item = db.scalar(select(Item).where(Item.name == "Ada"))
        assert saved_item is not None
        assert saved_item.grade == 90.0


@pytest.mark.parametrize("invalid_grade", ["a", "90x", "NaN", "Infinity"])
def test_create_rejects_non_numeric_or_non_finite_grade(client, invalid_grade):
    response = client.post(
        "/settings/grade", json={"name": "Ada", "grade": invalid_grade}
    )

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_create_duplicate_name_is_case_insensitive(client):
    client.post("/settings/grade", json={"name": "Ada", "grade": 90})

    response = client.post("/settings/grade", json={"name": " ada ", "grade": 95})

    assert response.status_code == 409


def test_patch_updates_grade_and_returns_numeric_data(client):
    client.post("/settings/grade", json={"name": "Ada", "grade": 90})

    response = client.patch("/settings/grade", json={"name": "ada", "grade": 95})

    assert response.status_code == 200
    assert response.json() == [{"name": "Ada", "grade": 95.0}]


def test_patch_unknown_name_returns_404(client):
    response = client.patch("/settings/grade", json={"name": "Missing", "grade": 95})

    assert response.status_code == 404
    assert response.json() == {"detail": "Grade for Missing not found."}


def test_put_updates_record(client):
    client.post("/settings/grade", json={"name": "Ada", "grade": 90})
    client.post("/settings/grade", json={"name": "Grace", "grade": 88})

    updated = client.put("/settings/grade", json={"name": "Ada", "grade": 95})

    assert updated.status_code == 200
    assert updated.json() == [
        {"name": "Ada", "grade": 95.0},
        {"name": "Grace", "grade": 88.0},
    ]


def test_put_unknown_name_returns_404(client):
    response = client.put("/settings/grade", json={"name": "Missing", "grade": 95})

    assert response.status_code == 404


def test_list_and_get_grades_return_database_records(client):
    client.post("/settings/grade", json={"name": "Ada", "grade": 90})
    client.post("/settings/grade", json={"name": "Grace", "grade": 88})

    all_grades = client.get("/settings/grade")
    one_grade = client.get("/settings/grade/ada")

    assert all_grades.status_code == 200
    assert all_grades.json() == [
        {"name": "Ada", "grade": 90.0},
        {"name": "Grace", "grade": 88.0},
    ]
    assert one_grade.status_code == 200
    assert one_grade.json() == {"name": "Ada", "grade": 90.0}


def test_get_unknown_grade_returns_404(client):
    response = client.get("/settings/grade/Missing")

    assert response.status_code == 404


def test_delete_grades_clears_database(client):
    client.post("/settings/grade", json={"name": "Ada", "grade": 90})

    response = client.delete("/settings/grade")

    assert response.status_code == 200
    assert response.json() == {"message": "All grades deleted."}
    assert client.get("/settings/grade").json() == []


def test_grade_import_converts_values_and_is_idempotent(
    test_sessions, tmp_path, monkeypatch
):
    grade_file = tmp_path / "grades.json"
    grade_file.write_text(
        json.dumps(
            [
                {"name": "Ada", "grade": "90"},
                {"name": "Grace", "grade": 88},
                {"name": " ada ", "grade": "91"},
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(import_grades, "GRADE_FILE", grade_file)
    monkeypatch.setattr(import_grades, "SessionLocal", test_sessions)

    first_run = import_grades.import_grades()
    second_run = import_grades.import_grades()

    assert first_run == (2, 1)
    assert second_run == (0, 3)
    with test_sessions() as db:
        assert [(item.name, item.grade) for item in db.scalars(select(Item))] == [
            ("Ada", 90.0),
            ("Grace", 88.0),
        ]


def test_grade_import_rolls_back_invalid_input(test_sessions, tmp_path, monkeypatch):
    grade_file = tmp_path / "grades.json"
    grade_file.write_text(
        json.dumps(
            [
                {"name": "Valid", "grade": "90"},
                {"name": "Invalid", "grade": "A"},
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(import_grades, "GRADE_FILE", grade_file)
    monkeypatch.setattr(import_grades, "SessionLocal", test_sessions)

    with pytest.raises(ValueError, match="Invalid numeric grade"):
        import_grades.import_grades()

    with test_sessions() as db:
        assert list(db.scalars(select(Item))) == []


def test_home_page_has_digits_only_grade_input_and_safe_error_display(client):
    response = client.get("/home")

    assert response.status_code == 200
    assert 'inputmode="numeric"' in response.text
    assert 'pattern="[0-9]+"' in response.text
    assert 'replace(/[^0-9]/g, "")' in response.text
    assert "Array.isArray(detail)" in response.text
    assert "error.msg" in response.text
    assert ".join(String.fromCharCode(10))" in response.text


def test_logout_redirects_to_home(client):
    response = client.post("/logout", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_invalid_endpoint_returns_404(client):
    response = client.get("/invalid-endpoint")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
