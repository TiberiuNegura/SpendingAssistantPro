# New Endpoint: Get All User Data

## 📊 GET /user/data

Retrieve complete spending data for the authenticated user with comprehensive statistics.

### Authentication
**Required:** JWT Bearer Token

### Parameters
None

### Response Schema

```json
{
  "username": "string",
  "total_spendings": "integer",
  "total_amount": "float",
  "category_breakdown": [
    {
      "category": "string",
      "total": "float"
    }
  ],
  "recent_spendings": [
    {
      "id": "integer",
      "user_id": "integer",
      "category": "string",
      "amount": "float",
      "created_at": "datetime"
    }
  ],
  "earliest_spending": "datetime",
  "latest_spending": "datetime"
}
```

### Example Request

```bash
curl -X GET "http://localhost:8000/user/data" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Example Response

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
    },
    {
      "category": "Lifestyle",
      "total": 220.00
    },
    {
      "category": "Utilities",
      "total": 150.00
    },
    {
      "category": "Entertainment",
      "total": 50.00
    }
  ],
  "recent_spendings": [
    {
      "id": 45,
      "user_id": 1,
      "category": "Groceries",
      "amount": 25.50,
      "created_at": "2026-01-30T14:30:00Z"
    },
    {
      "id": 44,
      "user_id": 1,
      "category": "Transportation",
      "amount": 45.00,
      "created_at": "2026-01-30T10:15:00Z"
    }
    // ... up to 10 most recent spendings
  ],
  "earliest_spending": "2026-01-01T08:00:00Z",
  "latest_spending": "2026-01-30T14:30:00Z"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `username` | string | The authenticated user's username |
| `total_spendings` | integer | Total number of spending records |
| `total_amount` | float | Sum of all spending amounts |
| `category_breakdown` | array | Total spending per category (sorted by amount) |
| `recent_spendings` | array | Last 10 spending records (sorted by date, newest first) |
| `earliest_spending` | datetime | Date of the earliest spending record |
| `latest_spending` | datetime | Date of the most recent spending record |

### Use Cases

1. **Dashboard Overview**: Display user's complete spending summary
2. **Profile Page**: Show user statistics and activity
3. **Analytics**: Visualize spending patterns over time
4. **Budget Planning**: Review total spending and category breakdown
5. **Activity Feed**: Show recent spending activity

### Features

✅ Complete spending statistics  
✅ Category breakdown (sorted by amount)  
✅ Recent activity (last 10 transactions)  
✅ Time range (earliest to latest)  
✅ All data in one request  

### Error Responses

**401 Unauthorized**
```json
{
  "detail": "Not authenticated"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Error message"
}
```

### Integration Example (JavaScript)

```javascript
async function getUserData(token) {
  const response = await fetch('http://localhost:8000/user/data', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch user data');
  }
  
  const data = await response.json();
  
  // Display summary
  console.log(`Total Spent: $${data.total_amount.toFixed(2)}`);
  console.log(`Number of Transactions: ${data.total_spendings}`);
  
  // Display category breakdown
  data.category_breakdown.forEach(cat => {
    console.log(`${cat.category}: $${cat.total.toFixed(2)}`);
  });
  
  return data;
}
```

### Integration Example (Python)

```python
import requests

def get_user_data(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        'http://localhost:8000/user/data',
        headers=headers
    )
    response.raise_for_status()
    return response.json()

# Usage
data = get_user_data(your_token)
print(f"Total Spent: ${data['total_amount']:.2f}")
print(f"Total Transactions: {data['total_spendings']}")

for category in data['category_breakdown']:
    print(f"{category['category']}: ${category['total']:.2f}")
```

### Comparison with Other Endpoints

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `GET /spendings` | List all spendings | Individual spending records (with filters) |
| `GET /spendings/totals` | Category totals | Aggregated totals per category |
| **`GET /user/data`** | **Complete overview** | **Everything: stats + breakdown + recent activity** |

### Performance

- **Response Time**: ~10-50ms (depends on number of records)
- **Database Queries**: 1 query to fetch all user spendings
- **Recommended Use**: Dashboard/profile pages, periodic refresh
- **Caching**: Consider caching this response on the client side

### Notes

- Returns empty arrays if user has no spending records
- `earliest_spending` and `latest_spending` are `null` if no records exist
- `recent_spendings` limited to 10 most recent records
- Category breakdown sorted by total amount (highest first)
- All dates in UTC timezone

---

## Quick Test

```bash
# After logging in and processing some receipts
curl -X GET "http://localhost:8000/user/data" \
  -H "Authorization: Bearer YOUR_TOKEN" | python -m json.tool
```

This endpoint is perfect for building user dashboards and analytics views! 📊
