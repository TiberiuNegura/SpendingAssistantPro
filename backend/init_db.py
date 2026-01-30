"""
Database initialization script
Recreates the database with the new spending tracking schema
"""
from app.database import engine, Base
import app.models  # Import models to register them with Base

def init_database():
    """
    Initialize or recreate the database with all tables
    """
    print("Initializing database...")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully!")
    print("Tables created: users, spendings")

if __name__ == "__main__":
    init_database()
