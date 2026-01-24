from transformers import pipeline

# 1. Initialize the classifier (do this once at the top of your script)
# 'facebook/bart-large-mnli' is the standard model for this task
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define your custom categories
candidate_labels = ["Groceries", "Entertainment", "Lifestyle", "Transportation", "Utilities"]


def categorize_receipt_data(json_data):
    items = json_data.get("menu", [])

    for item in items:
        # Extract the name string (handling the list structure in your JSON)
        raw_name = item.get("nm", [""])[0]

        # Clean up the name (remove extra spaces)
        clean_name = raw_name.strip()

        # Skip empty or date fields if possible
        if not clean_name or "DATE:" in clean_name:
            item["category"] = "Metadata"
            continue

        # Perform classification
        result = classifier(
            clean_name,
            candidate_labels,
            hypothesis_template="This is a purchase of {}."
        )

        # The model returns scores; the first label is the highest confidence
        top_category = result['labels'][0]
        confidence = result['scores'][0]

        # You can set a threshold, e.g., if confidence < 0.4, mark as 'Other'
        if confidence > 0.4:
            item["category"] = top_category
        else:
            item["category"] = "Other"

    return json_data


# --- Example Usage with your data ---
data = {
  "menu": [
    {
      "nm": [
        " DATE: 10/25/2024"
      ],
      "unitprice": [
        " Spennarket</s_nm><s_unitprice> 10/25/2024"
      ],
      "cnt": [
        " 2"
      ],
      "price": [
        " 1.00"
      ]
    },
    {
      "nm": [
        " BANANA"
      ],
      "unitprice": [
        " 1.50"
      ],
      "cnt": [
        " 3"
      ],
      "price": [
        " 1.20"
      ]
    },
    {
      "nm": [
        " ORANGE"
      ],
      "cnt": [
        " 2"
      ],
      "price": [
        " 0.75"
      ]
    },
    {
      "nm": [
        " PEAR"
      ],
      "cnt": [
        " 1"
      ],
      "price": [
        " 3.00"
      ]
    },
    {
      "nm": [
        " GRAPES"
      ],
      "cnt": [
        " 2"
      ],
      "price": [
        " 2.50"
      ]
    },
    {
      "nm": [
        " STRAWBERRY"
      ],
      "cnt": [
        " 1"
      ],
      "price": [
        " 2.00"
      ]
    },
    {
      "nm": [
        " BLUEBERRY"
      ],
      "cnt": [
        " 1"
      ],
      "price": [
        " 1.80"
      ]
    },
    {
      "nm": [
        " KIWI"
      ],
      "cnt": [
        " 2"
      ],
      "price": [
        " 1.80"
      ]
    },
    {
      "nm": [
        " WATERMELON"
      ],
      "cnt": [
        " 1"
      ],
      "price": [
        " 4.50"
      ]
    },
    {
      "nm": [
        " LEMON"
      ],
      "cnt": [
        " 1"
      ],
      "price": [
        " 0.60"
      ]
    },
    {
      "nm": [
        " RASPBERRY"
      ],
      "cnt": [
        " 1"
      ],
      "price": [
        " 3.00"
      ]
    },
    {
      "nm": [
        " MILK"
      ],
      "cnt": [
        " 1"
      ],
      "price": [
        " 1.50"
      ]
    },
    {
      "nm": [
        " CHEESE"
      ],
      "cnt": [
        " 1"
      ],
      "price": [
        " 2.80"
      ]
    },
    {
      "nm": [
        " YOGURT"
      ],
      "cnt": [
        " 1"
      ],
      "price": [
        " 1.20"
      ]
    }
  ],
  "total": {
    "total_price": " 27.35",
    "cashprice": " 30.00",
    "changeprice": " 2.65"
  }
}
enriched_data = categorize_receipt_data(data)

if __name__ == "__main__":
    for item in enriched_data['menu']:
        name = item['nm'][0].strip()
        cat = item.get('category')
        print(f"Item: {name:<15} | Category: {cat}")