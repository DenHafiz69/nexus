import os
import pytest
from fastapi.testclient import TestClient

# Mock DATABASE_URL before importing database and main so it uses SQLite for testing
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Set up an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_read_root():
    response = client.get("/")
    # Not testing full content since it requires templates, but should return 200
    assert response.status_code == 200

def test_shorten_url():
    response = client.post("/shorten", data={"url": "https://example.com"})
    assert response.status_code == 200
    assert b"href=" in response.content
    
def test_redirect_url():
    # First create a shortened URL
    post_response = client.post("/shorten", data={"url": "https://example.com"})
    assert post_response.status_code == 200
    
    # Inspect the db for the code since HTML is returned
    db = TestingSessionLocal()
    from app.models import URLItem
    item = db.query(URLItem).first()
    assert item is not None
    db.close()
    
    # Test redirect
    response = client.get(f"/{item.short_code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com"

def test_generate_qr():
    response = client.post("/generate-qr", data={"text": "https://example.com"})
    assert response.status_code == 200
    assert b"data:image/png;base64," in response.content
