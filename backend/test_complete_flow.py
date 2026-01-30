"""
Test the complete API flow to verify data is being saved
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_complete_flow():
    print("=" * 70)
    print("Testing Complete API Flow")
    print("=" * 70)

    # Step 1: Register or login
    username = "testuser123"
    password = "testpass123"

    print("\n1. Registering user...")
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            print(f"   ✓ Registered: {response.json()}")
        else:
            print(f"   User might already exist, trying login...")
    except Exception as e:
        print(f"   Registration skipped: {e}")

    # Step 2: Login
    print("\n2. Logging in...")
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": username, "password": password}
    )

    if response.status_code != 200:
        print(f"   ✗ Login failed: {response.text}")
        return

    token_data = response.json()
    token = token_data["access_token"]
    print(f"   ✓ Got token: {token[:20]}...")

    # Step 3: Upload receipt
    print("\n3. Uploading receipt...")
    headers = {"Authorization": f"Bearer {token}"}

    with open("receipt_2.png", "rb") as f:
        files = {"file": f}
        response = requests.post(
            f"{BASE_URL}/extract",
            headers=headers,
            files=files
        )

    if response.status_code != 200:
        print(f"   ✗ Upload failed: {response.text}")
        return

    receipt_data = response.json()
    print(f"   ✓ Receipt processed!")
    print(f"\n   Response:")
    print(json.dumps(receipt_data, indent=2))

    # Step 4: Get user data
    print("\n4. Getting user data...")
    response = requests.get(
        f"{BASE_URL}/user/data",
        headers=headers
    )

    if response.status_code != 200:
        print(f"   ✗ Get data failed: {response.text}")
        return

    user_data = response.json()
    print(f"   ✓ User data retrieved!")
    print(f"\n   Summary:")
    print(f"   - Total spendings: {user_data['total_spendings']}")
    print(f"   - Total amount: ${user_data['total_amount']:.2f}")
    print(f"\n   Category Breakdown:")
    for cat in user_data['category_breakdown']:
        print(f"     - {cat['category']}: ${cat['total']:.2f}")

    # Step 5: Get spendings list
    print("\n5. Getting spendings list...")
    response = requests.get(
        f"{BASE_URL}/spendings",
        headers=headers
    )

    if response.status_code != 200:
        print(f"   ✗ Get spendings failed: {response.text}")
        return

    spendings = response.json()
    print(f"   ✓ Found {len(spendings)} spending records")

    if spendings:
        print(f"\n   Recent spendings:")
        for spending in spendings[:5]:
            print(f"     - {spending['category']}: ${spending['amount']:.2f} ({spending['created_at']})")

    print("\n" + "=" * 70)
    print("✓ All tests passed!")
    print("=" * 70)

if __name__ == "__main__":
    test_complete_flow()
