# Spending Assistant Pro - Backend

## Overview
Backend API for the Spending Assistant Pro application with receipt scanning, categorization, and spending tracking.

## Features

### 🎯 Complete Receipt Processing Flow
1. **Client scans receipt** → Uploads image to server
2. **Server extracts data** → Uses Donut AI model to extract text and items
3. **Server classifies items** → Categorizes using Zero-Shot Classification + Keyword Matching
4. **Server saves to database** → Stores spending totals per category for the user

### 🔐 Authentication
- JWT-based authentication
- User registration and login
- Protected endpoints

### 📊 Spending Categories
- **Groceries**: Food, drinks, supermarket items
- **Entertainment**: Movies, games, concerts, streaming
- **Lifestyle**: Clothing, beauty, dining, travel
- **Transportation**: Gas, taxi, parking, public transit
- **Utilities**: Electric, water, internet, phone bills

### 🗄️ Database Structure
- **users.db**: User authentication data
- **spendings**: User spending records with categories and timestamps

## API Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /token` - Login and get access token

### Receipt Processing
- `POST /extract` - Upload and process receipt (requires authentication)
  - Extracts data from receipt image
  - Classifies items into categories
  - Saves spending totals to database
  - Returns extracted data + category totals

### Spending Queries
- `GET /spendings` - Get all user spendings
  - Query params: `category` (filter by category), `days` (last N days)
- `GET /spendings/totals` - Get total spending per category
  - Query params: `days` (last N days)
- `GET /user/data` - **NEW!** Get complete user data summary
  - Returns: Total statistics, category breakdown, recent activity, date range

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python init_db.py
```

### 3. Run Server
```bash
uvicorn main:app --reload
```

## Usage Example

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123"}'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=secret123"
```

### 3. Process Receipt
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@receipt.jpg"
```

Response:
```json
{
  "extracted_by": "john",
  "data": {
    "menu": [
      {
        "nm": ["Coffee"],
        "price": ["3.50"],
        "category": "Groceries"
      }
    ]
  },
  "category_totals": {
    "Groceries": 15.50,
    "Transportation": 45.00
  },
  "message": "Receipt processed and spending saved successfully"
}
```

### 4. Get Spending Totals
```bash
curl -X GET "http://localhost:8000/spendings/totals?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Response:
```json
[
  {
    "category": "Groceries",
    "total": 250.75
  },
  {
    "category": "Transportation",
    "total": 180.50
  }
]
```

### 5. Get Complete User Data
```bash
curl -X GET "http://localhost:8000/user/data" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Response:
```json
{
  "username": "john",
  "total_spendings": 45,
  "total_amount": 1250.75,
  "category_breakdown": [
    {
      "category": "Groceries",
      "total": 450.25
    },
    {
      "category": "Transportation",
      "total": 380.50
    }
  ],
  "recent_spendings": [
    {
      "id": 45,
      "user_id": 1,
      "category": "Groceries",
      "amount": 25.50,
      "created_at": "2026-01-30T14:30:00Z"
    }
  ],
  "earliest_spending": "2026-01-01T08:00:00Z",
  "latest_spending": "2026-01-30T14:30:00Z"
}
```

## Usage Example

The classifier now uses a **two-stage approach** for better accuracy:

1. **Keyword Matching** (Fast & Accurate)
   - Matches items against predefined keywords for each category
   - Scores each category based on keyword matches
   - Returns the category with the highest score

2. **Zero-Shot Classification** (Fallback)
   - Uses BART-large-MNLI model for items not matched by keywords
   - Applies confidence threshold (>0.35)
   - Defaults to "Other" for low-confidence predictions

### Benefits
- ✅ Faster processing (keyword matching is instant)
- ✅ More accurate categorization
- ✅ Better handling of common items
- ✅ Robust fallback for unusual items

## Technologies
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Transformers**: Hugging Face models (Donut + BART)
- **PyTorch**: Deep learning backend
- **JWT**: Authentication tokens
- **SQLite**: Database

## File Structure
```
backend/
├── main.py                 # FastAPI app & startup
├── classifier.py           # Receipt extraction & classification
├── init_db.py             # Database initialization
├── requirements.txt       # Python dependencies
├── users.db              # User database (created on first run)
└── app/
    ├── models.py         # SQLAlchemy models (User, Spending)
    ├── schemas.py        # Pydantic schemas
    ├── database.py       # Database connection
    ├── auth.py          # Authentication logic
    └── routers/
        ├── auth.py      # Auth endpoints
        └── receipts.py  # Receipt processing endpoints
```

## Notes
- The AI models will download automatically on first run (~500MB)
- Supports MPS (Apple Silicon), CUDA (NVIDIA), and CPU
- All spending data is user-specific and protected by authentication
- Timestamps are stored in UTC timezone
