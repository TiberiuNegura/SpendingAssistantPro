# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Setup
```bash
cd backend
pip install -r requirements.txt
python init_db.py
```

### Step 2: Run Server
```bash
uvicorn main:app --reload
```
Server runs at: http://localhost:8000

### Step 3: Test (in another terminal)
```bash
./test_api.sh
```

---

## 📱 Client Usage Flow

### 1. Register User
**Endpoint:** `POST /register`

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "pass123"}'
```

**Response:**
```json
{
  "username": "john"
}
```

---

### 2. Login
**Endpoint:** `POST /token`

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=pass123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

💡 **Save this token!** Use it in all subsequent requests.

---

### 3. Process Receipt
**Endpoint:** `POST /extract`

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@receipt.jpg"
```

**Response:**
```json
{
  "extracted_by": "john",
  "data": {
    "menu": [
      {
        "nm": ["Coffee"],
        "price": ["3.50"],
        "category": "Groceries"
      },
      {
        "nm": ["Gas"],
        "price": ["45.00"],
        "category": "Transportation"
      }
    ]
  },
  "category_totals": {
    "Groceries": 3.50,
    "Transportation": 45.00
  },
  "message": "Receipt processed and spending saved successfully"
}
```

✅ **Data is automatically saved to database!**

---

### 4. Get Spending Totals
**Endpoint:** `GET /spendings/totals`

```bash
# All time totals
curl -X GET "http://localhost:8000/spendings/totals" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Last 30 days
curl -X GET "http://localhost:8000/spendings/totals?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "category": "Groceries",
    "total": 250.75
  },
  {
    "category": "Transportation",
    "total": 180.50
  },
  {
    "category": "Lifestyle",
    "total": 120.00
  }
]
```

---

### 5. Get All Spendings
**Endpoint:** `GET /spendings`

```bash
# All spendings
curl -X GET "http://localhost:8000/spendings" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by category
curl -X GET "http://localhost:8000/spendings?category=Groceries" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Last 7 days
curl -X GET "http://localhost:8000/spendings?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "category": "Groceries",
    "amount": 25.50,
    "created_at": "2026-01-30T10:30:00Z"
  },
  {
    "id": 2,
    "user_id": 1,
    "category": "Transportation",
    "amount": 45.00,
    "created_at": "2026-01-30T10:30:00Z"
  }
]
```

---

## 🎯 Categories

The system automatically categorizes items into:

- **Groceries**: Food, drinks, supermarket items
- **Entertainment**: Movies, games, concerts
- **Lifestyle**: Clothing, restaurants, gym, travel
- **Transportation**: Gas, taxi, parking, public transit
- **Utilities**: Electric, water, internet, phone bills

---

## 🧪 Testing

### Test Classifier Only
```bash
python test_classifier.py
```

### Test Full API Flow
```bash
./test_api.sh
```

### Manual Test with Python
```python
from classifier import ReceiptExtractor

extractor = ReceiptExtractor()
data = extractor.process_receipt("receipt.jpg")
totals = extractor.calculate_category_totals(data)
print(totals)
```

---

## 🔧 Configuration

### Change JWT Secret
Edit `app/auth.py`:
```python
SECRET_KEY = "your-secret-key-here"
```

### Change Token Expiry
Edit `app/auth.py`:
```python
ACCESS_TOKEN_EXPIRE_DAYS = 30  # Change to desired days
```

### Change Database Location
Edit `app/database.py`:
```python
DATABASE_URL = "sqlite:///./users.db"  # Change path
```

---

## 📊 Query Parameters

### `/spendings` & `/spendings/totals`

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `days` | int | Last N days | `?days=30` |
| `category` | str | Filter category | `?category=Groceries` |

**Combine them:**
```bash
/spendings?category=Groceries&days=7
```

---

## 🐛 Troubleshooting

### Model not loading?
- Ensure PyTorch is installed: `pip install torch`
- Check internet connection (models download on first run)
- Free space needed: ~500MB

### Database errors?
- Run: `python init_db.py`
- Delete `users.db` and recreate

### Authentication errors?
- Check token is included: `Authorization: Bearer {token}`
- Token might be expired (30 days default)
- Re-login to get new token

### Receipt processing errors?
- Ensure image is clear and well-lit
- Supported formats: JPG, PNG
- Max file size: depends on FastAPI config

---

## 📚 Documentation Files

- **README.md**: Complete documentation
- **IMPROVEMENTS.md**: What was implemented
- **ARCHITECTURE.md**: System architecture diagrams
- **QUICKSTART.md**: This file

---

## 🎁 Features Summary

✅ AI-powered receipt extraction (Donut)  
✅ Smart categorization (Keywords + Zero-Shot)  
✅ User authentication (JWT)  
✅ Spending database (SQLite)  
✅ Time-based queries  
✅ Category filtering  
✅ Automatic totals calculation  
✅ Production-ready API  

---

## 💡 Tips

1. **Save your token** - You'll need it for all requests
2. **Clear photos** - Better lighting = better extraction
3. **Check totals** - Verify extracted amounts match receipt
4. **Use filters** - Query by category or time range
5. **Test first** - Use test scripts before building client

---

## 🚀 Next Steps

1. ✅ Test the API with the provided scripts
2. ✅ Try uploading your own receipts
3. ✅ Build a mobile/web client
4. ✅ Add more features (budgets, alerts, etc.)

---

**Need help?** Check the other documentation files:
- Detailed API docs: `README.md`
- Architecture info: `ARCHITECTURE.md`
- Implementation details: `IMPROVEMENTS.md`
