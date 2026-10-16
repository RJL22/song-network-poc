import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def test_authenticated_connection_is_idempotent_and_symmetric():
    with TestClient(app) as client:
        assert client.post("/auth/signup", json={"username": "alice", "password": "password"}).status_code == 200
        login = client.post("/auth/login", json={"username": "alice", "password": "password"})
        assert login.status_code == 200
        assert "access_token" in client.cookies

        song_a = client.post("/songs/", json={"mb_id": "a", "title": "A", "artist": "Artist"}).json()
        song_b = client.post("/songs/", json={"mb_id": "b", "title": "B", "artist": "Artist"}).json()

        first = client.post("/connections/", json={"song_1_id": song_b["id"], "song_2_id": song_a["id"]}).json()
        second = client.post("/connections/", json={"song_1_id": song_a["id"], "song_2_id": song_b["id"]}).json()

        assert first["id"] == second["id"]
        assert first["song_1_id"] < first["song_2_id"]
        history = client.get("/connections/mine")
        assert history.status_code == 200
        assert len(history.json()) == 1


def test_public_search_and_supporters():
    with TestClient(app) as client:
        assert client.post("/auth/signup", json={"username": "alice", "password": "password"}).status_code == 200
        assert client.post("/auth/login", json={"username": "alice", "password": "password"}).status_code == 200
        song_a = client.post("/songs/", json={"mb_id": "a", "title": "A", "artist": "Artist"}).json()
        song_b = client.post("/songs/", json={"mb_id": "b", "title": "B", "artist": "Artist"}).json()
        connection = client.post(
            "/connections/",
            json={"song_1_id": song_a["id"], "song_2_id": song_b["id"]},
        )
        assert connection.status_code == 200

        search = client.get("/songs/search", params={"title": "A"})
        assert search.status_code == 200
        assert search.json()[0]["title"] == "A"

        connections = client.get("/connections/")
        assert connections.status_code == 200
        connection_id = connections.json()[0]["id"]
        supporters = client.get(f"/connections/{connection_id}/supporters")
        assert supporters.status_code == 200
        assert supporters.json()[0]["username"] == "alice"
