import os
import sys


# Add the root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)


def test_upload_image():
    """Test the /upload endpoint."""
    # Upload a test image
    with open("data/test.tiff", "rb") as file:
        response = client.post("/upload", files={"file": ("test.tiff", file)})

    # Assert the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert the response contains the expected fields
    assert "filename" in response.json()
    assert "id" in response.json()

    # Assert the filename matches the uploaded file
    assert response.json()["filename"] == "test.tiff"


def test_get_metadata():
    """Test the /metadata/{image_id} endpoint."""
    # Upload a test image first (to ensure there's metadata to retrieve)
    with open("data/test.tiff", "rb") as file:
        upload_response = client.post("/upload", files={"file": ("test.tiff", file)})

    # Get the image ID from the upload response
    image_id = upload_response.json()["id"]
    print(image_id)

    # Retrieve metadata for the uploaded image
    response = client.get(f"/metadata/{image_id}")

    # Assert the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert the response contains the expected fields
    assert "filename" in response.json()
    assert "dimensions" in response.json()
    assert "num_bands" in response.json()

    # Assert the filename matches the uploaded file
    assert response.json()["filename"] == "test.tiff"


def test_get_slice():
    """Test the /slice endpoint."""
    # Upload a test image first
    with open("data/test.tiff", "rb") as file:
        upload_response = client.post("/upload", files={"file": ("test.tiff", file)})

    # Get the filename from the upload response
    filename = upload_response.json()["filename"]

    # Extract a slice (e.g., channel 0)
    response = client.get(f"/slice?filename={filename}&channel=0")

    # Assert the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert the response contains a valid slice
    response_data = response.json()
    assert "slice" in response_data  # Check if the "slice" key exists
    assert isinstance(response_data["slice"], list)  # The slice should be a list of lists


def test_get_statistics():
    """Test the /statistics endpoint."""
    # Upload a test image first
    with open("data/test.tiff", "rb") as file:
        upload_response = client.post("/upload", files={"file": ("test.tiff", file)})

    # Get the filename from the upload response
    filename = upload_response.json()["filename"]

    # Retrieve statistics for the uploaded image
    response = client.get(f"/statistics?filename={filename}")

    # Assert the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert the response contains the expected fields
    assert "mean" in response.json()
    assert "std" in response.json()
    assert "min" in response.json()
    assert "max" in response.json()


def test_upload_invalid_file():
    """Test uploading a file with an invalid format."""
    # Upload a non-TIFF file
    with open("data/invalid_file.txt", "rb") as file:
        response = client.post("/upload", files={"file": ("invalid_file.txt", file)})

    # Assert the response status code is 400 (Bad Request)
    assert response.status_code == 400

    # Assert the response contains an error message
    assert "detail" in response.json()
    assert "File must be a TIFF image" in response.json()["detail"]