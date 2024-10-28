import os
from database import Base, engine

# Check if the environment variable DROP_ALL_TABLES is set to "true"
overwrite_tables = os.getenv("OVERWRITE_TABLES", "false").lower() == "true"

if overwrite_tables:
    # Drop all existing tables
    print("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)

# Create all tables
print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("Database initialization complete.")