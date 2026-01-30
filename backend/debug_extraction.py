"""
Debug script to see exactly what data is being extracted
"""
import json
from classifier import ReceiptExtractor

def debug_extraction():
    print("=" * 70)
    print("DEBUG: Receipt Extraction & Category Totals")
    print("=" * 70)

    # Initialize extractor
    print("\n1. Loading models...")
    extractor = ReceiptExtractor()

    # Process receipt
    receipt_path = 'receipt_2.png'
    print(f"\n2. Processing: {receipt_path}")
    extracted_data = extractor.process_receipt(receipt_path)

    if not extracted_data:
        print("ERROR: No data extracted!")
        return

    # Show full extracted data
    print("\n3. Full Extracted Data:")
    print(json.dumps(extracted_data, indent=2))

    # Show individual items
    print("\n4. Menu Items Detail:")
    print("-" * 70)
    items = extracted_data.get('menu', [])
    for i, item in enumerate(items, 1):
        print(f"\nItem {i}:")
        print(f"  Raw data: {item}")
        print(f"  Name: {item.get('nm', ['N/A'])}")
        print(f"  Price: {item.get('price', ['N/A'])}")
        print(f"  Unit Price: {item.get('unitprice', ['N/A'])}")
        print(f"  Category: {item.get('category', 'N/A')}")

    # Show total section
    print("\n5. Total Section:")
    print("-" * 70)
    if 'total' in extracted_data:
        print(json.dumps(extracted_data['total'], indent=2))
    else:
        print("No total section found")

    # Show sub_total section
    print("\n6. Sub-Total Section:")
    print("-" * 70)
    if 'sub_total' in extracted_data:
        print(json.dumps(extracted_data['sub_total'], indent=2))
    else:
        print("No sub_total section found")

    # Calculate category totals
    print("\n7. Category Totals Calculation:")
    print("-" * 70)
    category_totals = extractor.calculate_category_totals(extracted_data)

    if category_totals:
        print("SUCCESS! Category totals:")
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: ${amount:.2f}")
        print(f"\nGrand Total: ${sum(category_totals.values()):.2f}")
    else:
        print("WARNING: No category totals calculated!")
        print("\nTrying manual total extraction...")
        total = extractor._extract_total_price(extracted_data)
        print(f"Manual extraction got: ${total:.2f}")

    print("\n" + "=" * 70)
    print("Debug complete!")
    print("=" * 70)

if __name__ == "__main__":
    debug_extraction()
