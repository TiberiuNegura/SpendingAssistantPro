# --- FastAPI Application ---
import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from starlette.responses import JSONResponse

from receipts_extractor import ReceiptExtractor

app = FastAPI()

# Load the model on server startup
# This ensures we don't reload the model for every request.
try:
    extractor = ReceiptExtractor()
except Exception as e:
    print(f"Failed to load model on startup: {e}")
    # If the model can't load, the app is not useful.
    # In a real-world scenario, you might want to handle this more gracefully.
    extractor = None


@app.on_event("startup")
async def startup_event():
    global extractor
    if extractor is None:
        print("Retrying model load on startup...")
        try:
            extractor = ReceiptExtractor()
        except Exception as e:
            print(f"Failed to load model on startup: {e}")
            extractor = None


@app.get("/ping")
def ping():
    """A simple endpoint to check if the server is running."""
    return {"message": "pong"}


@app.post("/extract")
async def extract_receipt_data(file: UploadFile = File(...)):
    """
    Upload a receipt image and get the extracted JSON data.
    """
    if extractor is None:
        raise HTTPException(status_code=503,
                            detail="Model is not loaded. Server might be starting or an error occurred.")

    # Define a temporary file path
    temp_path = f"temp_{file.filename}"

    try:
        # Save the uploaded file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the saved file
        print(f"Processing {temp_path}...")
        extracted_data = extractor.process_receipt(temp_path)

        if not extracted_data:
            # Handle cases where parsing might fail
            raise HTTPException(status_code=400,
                                detail="Could not extract data. Image may be unclear or not a valid receipt.")

        # Return the successful extraction. FastAPI handles dict -> JSON.
        return extracted_data

    except Exception as e:
        # Catch any other unexpected errors
        print(f"An error occurred: {e}")
        # Return a JSONResponse for clarity
        return JSONResponse(
            status_code=500,
            content={"error": f"An internal server error occurred: {str(e)}"}
        )
    finally:
        # Ensure the temporary file is always deleted
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # Close the uploaded file
        await file.close()