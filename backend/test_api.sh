#!/bin/bash

# API Testing Script for Spending Assistant Pro
# This script demonstrates the complete flow

echo "==================================================================="
echo "Spending Assistant Pro - API Testing"
echo "==================================================================="

BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}Step 1: Register a new user${NC}"
echo "-------------------------------------------------------------------"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}')
echo "$REGISTER_RESPONSE" | python -m json.tool
echo ""

echo -e "\n${BLUE}Step 2: Login to get access token${NC}"
echo "-------------------------------------------------------------------"
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123")
echo "$TOKEN_RESPONSE" | python -m json.tool

# Extract token
TOKEN=$(echo "$TOKEN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "Failed to get token. User might already exist. Trying to login..."
    TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/token" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=testuser&password=testpass123")
    TOKEN=$(echo "$TOKEN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
fi

echo -e "\n${GREEN}Token obtained: ${TOKEN:0:20}...${NC}"

echo -e "\n${BLUE}Step 3: Process a receipt${NC}"
echo "-------------------------------------------------------------------"
RECEIPT_RESPONSE=$(curl -s -X POST "$BASE_URL/extract" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@receipt_2.png")
echo "$RECEIPT_RESPONSE" | python -m json.tool
echo ""

echo -e "\n${BLUE}Step 4: Get spending totals${NC}"
echo "-------------------------------------------------------------------"
TOTALS_RESPONSE=$(curl -s -X GET "$BASE_URL/spendings/totals" \
  -H "Authorization: Bearer $TOKEN")
echo "$TOTALS_RESPONSE" | python -m json.tool
echo ""

echo -e "\n${BLUE}Step 5: Get all spendings${NC}"
echo "-------------------------------------------------------------------"
SPENDINGS_RESPONSE=$(curl -s -X GET "$BASE_URL/spendings" \
  -H "Authorization: Bearer $TOKEN")
echo "$SPENDINGS_RESPONSE" | python -m json.tool
echo ""

echo -e "\n${BLUE}Step 6: Get complete user data summary${NC}"
echo "-------------------------------------------------------------------"
USER_DATA_RESPONSE=$(curl -s -X GET "$BASE_URL/user/data" \
  -H "Authorization: Bearer $TOKEN")
echo "$USER_DATA_RESPONSE" | python -m json.tool
echo ""

echo -e "\n${GREEN}==================================================================="
echo "Testing completed!"
echo "===================================================================${NC}"
