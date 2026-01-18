import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from app.auth import get_current_user
from app.models import User

router = APIRouter(tags=["Receipts"])


@router.post("/extract")
async def extract_receipt_data(
        request: Request,
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user)
):
    extractor = request.app.state.extractor
    if extractor is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extracted_data = extractor.process_receipt(temp_path)

        if not extracted_data:
            raise HTTPException(status_code=400, detail="Could not extract data.")

        # Return data with a note on who extracted it
        return {
            "extracted_by": current_user.username,
            "data": extracted_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        await file.close()