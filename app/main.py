from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from . import models
from .database import SessionLocal, engine
from .image_processor import HighDimImageProcessor
from .celery import process_image_async
import os
models.Base.metadata.create_all(bind=engine)
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
    file_path = f"data/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Load the image and extract metadata
    processor = HighDimImageProcessor(file_path)
    dimensions = ",".join(map(str, processor.dimensions))
    num_bands = processor.dimensions[-1]

    # Store metadata in the database
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