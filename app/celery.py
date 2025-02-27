from celery import Celery
from .image_processor import HighDimImageProcessor

app = Celery("image_processor", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@app.task
def process_image_async(image_path, operation, **kwargs):
    """Process an image asynchronously."""
    processor = HighDimImageProcessor(image_path)
    if operation == "pca":
        return processor.perform_pca(**kwargs).tolist()
    elif operation == "statistics":
        return processor.calculate_statistics()
    elif operation == "segment":
        return processor.segment_image(**kwargs).tolist()
    else:
        raise ValueError("Invalid operation")