from sqlalchemy import Column, Integer, String, JSON
from .database import Base

class ImageMetadata(Base):
    """Model for storing image metadata."""
    __tablename__ = "image_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    dimensions = Column(String)  # Store as a string (e.g., "X,Y,Z,Time,Channel")
    num_bands = Column(Integer)

class AnalysisResult(Base):
    """Model for storing analysis results."""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, index=True)
    operation = Column(String)  # E.g., "PCA", "Statistics", "Segmentation"
    result = Column(JSON)  # Store results as JSON (e.g., PCA components, statistics)