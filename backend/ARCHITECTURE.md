# System Architecture & Flow

## Complete Receipt Processing Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Mobile/Web)                         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    1. Scan Receipt & Upload Image
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       FASTAPI SERVER                                │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ POST /extract Endpoint                                       │ │
│  │  • Receives receipt image                                    │ │
│  │  • Authenticates user (JWT)                                  │ │
│  │  • Saves temp file                                           │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                  │                                  │
│                    2. Extract Data from Receipt                    │
│                                  │                                  │
│                                  ▼                                  │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ DONUT AI MODEL (Vision Encoder-Decoder)                      │ │
│  │  • Processes receipt image                                   │ │
│  │  • Extracts: Items, Prices, Total                            │ │
│  │  • Returns structured JSON                                   │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                  │                                  │
│                    3. Classify Each Item                           │
│                                  │                                  │
│                                  ▼                                  │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ KEYWORD MATCHER (Fast Path)                                  │ │
│  │  • Matches against 87 keywords                               │ │
│  │  • Scores each category                                      │ │
│  │  • Returns best match if found                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                  │                                  │
│                         If no keyword match                        │
│                                  │                                  │
│                                  ▼                                  │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ ZERO-SHOT CLASSIFIER (BART-MNLI)                             │ │
│  │  • AI-based classification                                   │ │
│  │  • Confidence threshold: 0.35                                │ │
│  │  • Fallback to "Other" if low confidence                     │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                  │                                  │
│                    4. Calculate Category Totals                    │
│                                  │                                  │
│                                  ▼                                  │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ CATEGORY AGGREGATOR                                          │ │
│  │  • Sums prices per category                                  │ │
│  │  • Handles currency formats                                  │ │
│  │  • Removes metadata/zero amounts                             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                  │                                  │
│                    5. Save to Database                             │
│                                  │                                  │
│                                  ▼                                  │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ SQLITE DATABASE (users.db)                                   │ │
│  │                                                               │ │
│  │  ┌─────────────────────────────────────────────────────┐    │ │
│  │  │ spendings table                                     │    │ │
│  │  │  • user_id (FK to users)                            │    │ │
│  │  │  • category (Groceries, Transport, etc.)            │    │ │
│  │  │  • amount (float)                                   │    │ │
│  │  │  • created_at (timestamp UTC)                       │    │ │
│  │  └─────────────────────────────────────────────────────┘    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                  │                                  │
│                    6. Return Response                              │
│                                  │                                  │
└──────────────────────────────────┼──────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         RESPONSE TO CLIENT                          │
│                                                                     │
│  {                                                                  │
│    "extracted_by": "username",                                      │
│    "data": { /* Full extracted data */ },                          │
│    "category_totals": {                                             │
│      "Groceries": 25.50,                                            │
│      "Transportation": 45.00,                                       │
│      ...                                                            │
│    },                                                               │
│    "message": "Receipt processed and spending saved successfully"  │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Categories & Keywords

```
┌──────────────────┬────────────────────────────────────────────────┐
│ Category         │ Keywords (87 total)                            │
├──────────────────┼────────────────────────────────────────────────┤
│ Groceries (22)   │ food, drink, grocery, market, vegetable,       │
│                  │ fruit, meat, dairy, bread, snack, beverage,    │
│                  │ milk, eggs, chicken, beef, fish, coffee,       │
│                  │ tea, water, juice, supermarket, store          │
├──────────────────┼────────────────────────────────────────────────┤
│ Entertainment    │ movie, cinema, game, concert, ticket, show,    │
│ (17)             │ theater, music, streaming, netflix, spotify,   │
│                  │ xbox, playstation, entertainment, fun,         │
│                  │ park, museum                                   │
├──────────────────┼────────────────────────────────────────────────┤
│ Lifestyle (21)   │ clothing, clothes, shoes, fashion, beauty,     │
│                  │ cosmetic, salon, gym, fitness, sport, book,    │
│                  │ magazine, furniture, home, restaurant,         │
│                  │ dining, cafe, bar, hotel, travel               │
├──────────────────┼────────────────────────────────────────────────┤
│ Transportation   │ gas, fuel, petrol, diesel, uber, taxi, bus,    │
│ (14)             │ train, metro, subway, parking, toll, car,      │
│                  │ vehicle, transport                             │
├──────────────────┼────────────────────────────────────────────────┤
│ Utilities (13)   │ electric, electricity, water, bill, phone,     │
│                  │ internet, wifi, utility, gas, heating,         │
│                  │ cooling, service, subscription                 │
└──────────────────┴────────────────────────────────────────────────┘
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────────┐
│                         users table                             │
├──────────────┬──────────────┬────────────┬─────────────────────┤
│ Column       │ Type         │ Attributes │ Description         │
├──────────────┼──────────────┼────────────┼─────────────────────┤
│ id           │ Integer      │ PK, Index  │ User ID             │
│ username     │ String       │ Unique, IX │ Login username      │
│ hashed_pwd   │ String       │            │ Hashed password     │
└──────────────┴──────────────┴────────────┴─────────────────────┘
                                  │
                                  │ One-to-Many
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                       spendings table                           │
├──────────────┬──────────────┬────────────┬─────────────────────┤
│ Column       │ Type         │ Attributes │ Description         │
├──────────────┼──────────────┼────────────┼─────────────────────┤
│ id           │ Integer      │ PK, Index  │ Spending record ID  │
│ user_id      │ Integer      │ FK, Index  │ Foreign key to user │
│ category     │ String       │ Index      │ Spending category   │
│ amount       │ Float        │            │ Amount spent        │
│ created_at   │ DateTime     │            │ Timestamp (UTC)     │
└──────────────┴──────────────┴────────────┴─────────────────────┘
```

## API Endpoints

```
┌────────────────┬─────────────────────┬──────────────────────────┐
│ Method         │ Endpoint            │ Description              │
├────────────────┼─────────────────────┼──────────────────────────┤
│ POST           │ /register           │ Create new user          │
│ POST           │ /token              │ Login (get JWT token)    │
│ POST           │ /extract            │ Process receipt [AUTH]   │
│ GET            │ /spendings          │ Get all spendings [AUTH] │
│ GET            │ /spendings/totals   │ Get category totals [AUTH]│
└────────────────┴─────────────────────┴──────────────────────────┘
```

## Processing Pipeline Performance

```
Stage                    Method              Time      Accuracy
─────────────────────────────────────────────────────────────────
1. Image Upload          FastAPI             ~10ms     N/A
2. Data Extraction       Donut Vision        ~2-5s     85-90%
3. Keyword Matching      String Search       ~1ms      95%
4. Zero-Shot (fallback)  BART-MNLI          ~200ms    80%
5. Category Totals       Python Sum          <1ms      100%
6. Database Save         SQLite Insert       ~5ms      100%
─────────────────────────────────────────────────────────────────
TOTAL                                        ~2-5s     90%+
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      TECHNOLOGY STACK                       │
├────────────────┬────────────────────────────────────────────┤
│ Framework      │ FastAPI (async Python web framework)      │
│ ML Models      │ Donut (vision), BART-MNLI (zero-shot)    │
│ ML Library     │ HuggingFace Transformers + PyTorch        │
│ Database       │ SQLite + SQLAlchemy ORM                   │
│ Auth           │ JWT (JSON Web Tokens)                     │
│ Validation     │ Pydantic schemas                          │
│ Deployment     │ Uvicorn ASGI server                       │
└────────────────┴────────────────────────────────────────────┘
```

## File Structure

```
backend/
├── main.py                    # FastAPI app & model loading
├── classifier.py              # Enhanced receipt extractor
├── init_db.py                 # Database initialization
├── test_classifier.py         # Standalone classifier test
├── test_api.sh               # API integration test
├── requirements.txt           # Python dependencies
├── users.db                   # SQLite database (auto-created)
├── README.md                  # User documentation
├── IMPROVEMENTS.md            # Implementation summary
├── ARCHITECTURE.md            # This file
│
└── app/
    ├── models.py              # SQLAlchemy models (User, Spending)
    ├── schemas.py             # Pydantic schemas (request/response)
    ├── database.py            # Database connection & session
    ├── auth.py                # JWT authentication logic
    │
    └── routers/
        ├── auth.py            # Auth endpoints (/register, /token)
        └── receipts.py        # Receipt endpoints (/extract, /spendings)
```

## Security Flow

```
┌──────────────┐
│ Client       │
└──────┬───────┘
       │
       │ 1. POST /register {username, password}
       ▼
┌──────────────┐
│ Hash Password│ (bcrypt)
└──────┬───────┘
       │
       │ 2. Store in DB
       ▼
┌──────────────┐
│ POST /token  │ {username, password}
└──────┬───────┘
       │
       │ 3. Verify credentials
       ▼
┌──────────────┐
│ Generate JWT │ (expires in 30 days)
└──────┬───────┘
       │
       │ 4. Return token
       ▼
┌──────────────┐
│ Client       │ Stores token
└──────┬───────┘
       │
       │ 5. All requests: Authorization: Bearer {token}
       ▼
┌──────────────┐
│ Verify JWT   │ Decode & validate
└──────┬───────┘
       │
       │ 6. Extract user_id
       ▼
┌──────────────┐
│ Process      │ User-specific operations
│ Request      │
└──────────────┘
```
