"""
Test script to demonstrate the improved classifier and complete flow
"""
import json
from classifier import ReceiptExtractor

def test_classifier():
    """
    Test the improved classifier with better categorization
    """
    print("=" * 60)
    print("Testing Improved Receipt Classifier")
    print("=" * 60)

    # Initialize the extractor (loads both Donut and BART models)
    print("\n1. Loading models...")
    extractor = ReceiptExtractor()

    # Test with a sample receipt
    receipt_path = 'receipt_2.png'

    print(f"\n2. Processing receipt: {receipt_path}")
    extracted_data = extractor.process_receipt(receipt_path)

    if extracted_data:
        print("\n3. Extracted & Categorized Data:")
        print(json.dumps(extracted_data, indent=2))

        print("\n4. Item Summary:")
        print("-" * 60)
        print(f"{'Item Name':<30} {'Price':<10} {'Category':<20}")
        print("-" * 60)

        for item in extracted_data.get('menu', []):
            name = item.get('nm', [''])[0].strip()
            price_data = item.get('price', item.get('unitprice', ['N/A']))
            price = price_data[0] if isinstance(price_data, list) else str(price_data)
            category = item.get('category', 'N/A')

            if name and category != "Metadata":
                print(f"{name:<30} ${price:<9} {category:<20}")

        print("-" * 60)

        print("\n5. Category Totals:")
        print("-" * 60)
        category_totals = extractor.calculate_category_totals(extracted_data)

        total_sum = 0
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            if category != "Metadata":
                print(f"{category:<30} ${amount:>10.2f}")
                total_sum += amount

        print("-" * 60)
        print(f"{'TOTAL':<30} ${total_sum:>10.2f}")
        print("-" * 60)

        print("\n✅ Test completed successfully!")
        print("\nThis data would now be saved to the database per user.")

    else:
        print(f"\n❌ Could not process the receipt at {receipt_path}")

if __name__ == "__main__":
    test_classifier()
