# High-Dimensional Image Processing System

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Run the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
## API Endpoints</br>
- POST /upload: Upload a multi-dimensional image.

- GET /metadata: Retrieve image metadata.

- GET /slice: Extract a specific slice.

- POST /analyze: Run PCA on the image.

- GET /statistics: Calculate image statistics. 