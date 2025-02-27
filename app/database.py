from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./image_data.db"

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Base class
Base = declarative_base()

# Function to initialize the database
def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)

# Call init_db() to create tables when this module is imported
init_db()