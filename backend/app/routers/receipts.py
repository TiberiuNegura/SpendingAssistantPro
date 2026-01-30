import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.auth import get_current_user
from app.models import User, Spending
from app.database import get_db
from app.schemas import SpendingResponse, CategoryTotal, UserDataSummary

router = APIRouter(tags=["Receipts"])


@router.post("/extract")
async def extract_receipt_data(
        request: Request,
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Complete flow: Extract receipt data -> Classify items -> Save spending to database
    """
    extractor = request.app.state.extractor
    if extractor is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    temp_path = f"temp_{file.filename}"
    try:
        # Save uploaded file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 1: Extract data from receipt
        extracted_data = extractor.process_receipt(temp_path)

        if not extracted_data:
            raise HTTPException(status_code=400, detail="Could not extract data from receipt.")

        # Step 2: Calculate category totals
        print(f"DEBUG: Calculating category totals...")
        category_totals = extractor.calculate_category_totals(extracted_data)
        print(f"DEBUG: Category totals: {category_totals}")

        # Step 3: Save spending to database
        saved_count = 0
        for category, amount in category_totals.items():
            if amount > 0 and category != "Metadata":  # Skip zero amounts and metadata
                spending = Spending(
                    user_id=current_user.id,
                    category=category,
                    amount=amount
                )
                db.add(spending)
                saved_count += 1
                print(f"DEBUG: Saved {category}: ${amount:.2f}")

        db.commit()
        print(f"DEBUG: Committed {saved_count} spending records to database")

        # Return comprehensive response
        return {
            "extracted_by": current_user.username,
            "data": extracted_data,
            "category_totals": category_totals,
            "message": f"Receipt processed and {saved_count} category totals saved successfully"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        await file.close()


@router.get("/spendings", response_model=List[SpendingResponse])
async def get_user_spendings(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
        category: str = None,
        days: int = None
):
    """
    Get all spendings for the current user, optionally filtered by category and time range
    """
    query = db.query(Spending).filter(Spending.user_id == current_user.id)

    if category:
        query = query.filter(Spending.category == category)

    if days:
        date_threshold = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Spending.created_at >= date_threshold)

    spendings = query.order_by(Spending.created_at.desc()).all()
    return spendings


@router.get("/spendings/totals", response_model=List[CategoryTotal])
async def get_category_totals(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
        days: int = None
):
    """
    Get total spending per category for the current user
    """
    query = db.query(Spending).filter(Spending.user_id == current_user.id)

    if days:
        date_threshold = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Spending.created_at >= date_threshold)

    spendings = query.all()

    # Calculate totals by category
    category_totals = {}
    for spending in spendings:
        if spending.category in category_totals:
            category_totals[spending.category] += spending.amount
        else:
            category_totals[spending.category] = spending.amount

    # Convert to list of CategoryTotal objects
    result = [
        CategoryTotal(category=category, total=total)
        for category, total in category_totals.items()
    ]

    return sorted(result, key=lambda x: x.total, reverse=True)


@router.get("/user/data", response_model=UserDataSummary)
async def get_all_user_data(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Get complete user spending data including statistics, category breakdown, and recent activity
    """
    # Get all spendings for the user
    all_spendings = db.query(Spending).filter(
        Spending.user_id == current_user.id
    ).order_by(Spending.created_at.desc()).all()

    # Calculate statistics
    total_spendings = len(all_spendings)
    total_amount = sum(spending.amount for spending in all_spendings)

    # Calculate category breakdown
    category_totals = {}
    for spending in all_spendings:
        if spending.category in category_totals:
            category_totals[spending.category] += spending.amount
        else:
            category_totals[spending.category] = spending.amount

    category_breakdown = [
        CategoryTotal(category=category, total=total)
        for category, total in category_totals.items()
    ]
    category_breakdown = sorted(category_breakdown, key=lambda x: x.total, reverse=True)

    # Get recent spendings (last 10)
    recent_spendings = all_spendings[:10]

    # Get earliest and latest spending dates
    earliest_spending = None
    latest_spending = None
    if all_spendings:
        earliest_spending = min(spending.created_at for spending in all_spendings)
        latest_spending = max(spending.created_at for spending in all_spendings)

    return UserDataSummary(
        username=current_user.username,
        total_spendings=total_spendings,
        total_amount=total_amount,
        category_breakdown=category_breakdown,
        recent_spendings=recent_spendings,
        earliest_spending=earliest_spending,
        latest_spending=latest_spending
    )

