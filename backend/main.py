from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, receipts

# Import the improved extractor class from classifier.py
try:
    from classifier import ReceiptExtractor
except ImportError:
    ReceiptExtractor = None
    print("Warning: classifier.py not found.")

# Create DB Tables
Base.metadata.create_all(bind=engine)


# Lifespan event to handle model loading on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the model
    try:
        app.state.extractor = ReceiptExtractor()
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Failed to load model: {e}")
        app.state.extractor = None

    yield

    # Shutdown: (Cleanup if needed)
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

# Include Routers
app.include_router(auth.router)
app.include_router(receipts.router)


@app.get("/ping")
def ping():
    return {"message": "pong"}