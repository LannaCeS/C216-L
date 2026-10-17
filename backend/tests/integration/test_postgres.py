import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, inspect, select
from sqlalchemy.orm import sessionmaker

from app.database.session import get_db
from app.main import app
from app.models.item import Item

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not TEST_DATABASE_URL,
        reason="Set TEST_DATABASE_URL to a disposable PostgreSQL test database.",
    ),
]


@pytest.fixture
def postgres_client():
    engine = create_engine(TEST_DATABASE_URL)
    if engine.dialect.name != "postgresql":
        engine.dispose()
        pytest.fail("TEST_DATABASE_URL must use PostgreSQL.")
    if "alunos" not in inspect(engine).get_table_names():
        engine.dispose()
        pytest.fail("Apply Alembic migrations to TEST_DATABASE_URL before testing.")

    test_sessions = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db():
        with test_sessions() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client, test_sessions
    finally:
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()


def test_grade_api_persists_and_reads_from_postgresql(postgres_client):
    client, test_sessions = postgres_client
    name = f"integration-{uuid4().hex}"
    try:
        created = client.post(
            "/settings/grade", json={"name": name, "grade": "91"}
        )
        fetched = client.get(f"/settings/grade/{name}")

        assert created.status_code == 200
        assert created.json() == [{"name": name, "grade": 91.0}]
        assert fetched.status_code == 200
        assert fetched.json() == {"name": name, "grade": 91.0}
        with test_sessions() as db:
            stored = db.scalar(select(Item).where(Item.name == name))
            assert stored is not None
            assert stored.grade == 91.0
    finally:
        with test_sessions() as db:
            db.execute(delete(Item).where(Item.name == name))
            db.commit()
