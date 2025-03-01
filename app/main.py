import io

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends,status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from . import models
from .database import SessionLocal, engine
from .image_processor import HighDimImageProcessor
from .celery import process_image_async
import os
from .database import init_db
init_db()

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a multi-dimensional image and store its metadata."""
    if not file.filename.endswith(".tiff"):
        raise HTTPException(status_code=400, detail="File must be a TIFF image.")

    # Create the data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Save the file (overwrite if it already exists)
    file_path = f"data/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Load the image and extract metadata
    processor = HighDimImageProcessor(file_path)
    dimensions = ",".join(map(str, processor.dimensions))
    num_bands = processor.dimensions[-1]

    # Check if metadata for the filename already exists
    db_image = db.query(models.ImageMetadata).filter(models.ImageMetadata.filename == file.filename).first()
    if db_image:
        # Update existing metadata
        db_image.dimensions = dimensions
        db_image.num_bands = num_bands
    else:
        # Insert new metadata
        db_image = models.ImageMetadata(
            filename=file.filename,
            dimensions=dimensions,
            num_bands=num_bands,
        )
        db.add(db_image)

    db.commit()
    db.refresh(db_image)

    return {"filename": file.filename, "id": db_image.id}

@app.get("/metadata/{image_id}")
async def get_metadata(image_id: int, db: Session = Depends(get_db)):
    """Retrieve image metadata from the database."""
    db_image = db.query(models.ImageMetadata).filter(models.ImageMetadata.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found.")
    return {
        "filename": db_image.filename,
        "dimensions": db_image.dimensions,
        "num_bands": db_image.num_bands,
    }

@app.get("/slice")
async def get_slice(
    filename: str,
    y: int = None,
    x: int = None,
    channel: int = None,
):
    """Extract a specific slice from a 3D image."""
    if not os.path.exists(f"data/{filename}"):
        raise HTTPException(status_code=404, detail="File not found.")

    # Load the image and get its dimensions
    processor = HighDimImageProcessor(f"data/{filename}")
    dimensions = processor.dimensions

    # Validate parameters
    if y is not None and (y < 0 or y >= dimensions[0]):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Y index. Must be between 0 and {dimensions[0] - 1}.",
        )
    if x is not None and (x < 0 or x >= dimensions[1]):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid X index. Must be between 0 and {dimensions[1] - 1}.",
        )
    if channel is not None and (channel < 0 or channel >= dimensions[2]):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Channel index. Must be between 0 and {dimensions[2] - 1}.",
        )

    # Extract the slice
    try:
        if y is not None:
            # Extract a row (Y-slice)
            slice_data = processor.image[y, :, :]
        elif x is not None:
            # Extract a column (X-slice)
            slice_data = processor.image[:, x, :]
        elif channel is not None:
            # Extract a channel
            slice_data = processor.image[:, :, channel]
        else:
            # Return the entire image if no parameters are provided
            slice_data = processor.image

        # Convert the NumPy array to a JSON-compatible format (nested list)
        slice_data_json = slice_data.tolist()

        return {"slice": slice_data_json}
    except IndexError:
        raise HTTPException(status_code=400, detail="Invalid slice parameters.")

@app.post("/analyze/{image_id}")
async def analyze_image(image_id: int, operation: str, db: Session = Depends(get_db)):
    """Run analysis on the image and store results in the database."""
    db_image = db.query(models.ImageMetadata).filter(models.ImageMetadata.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found.")

    # Trigger Celery task for asynchronous processing
    task = process_image_async.delay(f"data/{db_image.filename}", operation)
    return {"task_id": task.id}

@app.get("/task/{task_id}")
async def get_task_result(task_id: str):
    """Retrieve the result of an asynchronous task."""
    result = process_image_async.AsyncResult(task_id)
    if result.ready():
        return {"status": "completed", "result": result.result}
    else:
        return {"status": "pending"}

@app.get("/statistics")
async def get_statistics(filename: str):
    """Calculate image statistics."""
    if not os.path.exists(f"data/{filename}"):
        raise HTTPException(status_code=404, detail="File not found.")
    processor = HighDimImageProcessor(f"data/{filename}")
    try:
        stats = processor.calculate_statistics()
        return stats
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))