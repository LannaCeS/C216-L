import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base, get_db
from app.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5433/books_test",
)

# Trava de segurança: testes nunca rodam em um banco que não seja de teste
_db_name = TEST_DATABASE_URL.rsplit("/", 1)[-1].split("?")[0]
assert _db_name.endswith("_test"), (
    f"TEST_DATABASE_URL deve apontar para um banco terminado em _test, não '{_db_name}'"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSession = sessionmaker(bind=engine)


@pytest.fixture
def client():
    Base.metadata.create_all(engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
