import os
from dotenv import load_dotenv

# Load env before importing app modules
load_dotenv()

from app.database import engine, Base
# Import all models to ensure they are registered with Base
from app import models

# Print the URL to confirm it's using the right one
from app.core.config import settings
print(f"Using DATABASE_URL: {settings.DATABASE_URL}")

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
