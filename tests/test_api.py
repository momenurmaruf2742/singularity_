from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_image():
    response = client.post("/upload", files={"file": ("test.tiff", open("data/test.tiff", "rb"))})
    assert response.status_code == 200

def test_get_metadata():
    response = client.get("/metadata/1")
    assert response.status_code == 200