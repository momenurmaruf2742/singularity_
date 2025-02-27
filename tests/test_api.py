from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_image():
    response = client.post("/upload", files={"file": ("sample_5d_image.tiff", open("/media/maruf/f528ebe5-e2ce-445d-87cb-ce5208a8080d/personal/high_dim_image_processor/data/sample_5d_image.tiff", "rb"))})
    assert response.status_code == 200

def test_get_metadata():
    response = client.get("/metadata/1")
    assert response.status_code == 200