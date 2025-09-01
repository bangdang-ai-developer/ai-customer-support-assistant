#!/bin/bash

# BIWOCO AI Customer Support Assistant - API Test Script
# This script tests all major API endpoints

API_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "======================================"
echo "BIWOCO API Test Suite"
echo "======================================"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check Endpoint..."
HEALTH_RESPONSE=$(curl -s $API_URL/health)
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}✗ Health check failed${NC}"
fi
echo ""

# Test 2: API Documentation
echo "2. Testing API Documentation..."
DOC_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/docs)
if [[ $DOC_RESPONSE == "200" ]]; then
    echo -e "${GREEN}✓ API documentation accessible${NC}"
    echo "   URL: $API_URL/docs"
else
    echo -e "${RED}✗ API documentation not accessible${NC}"
fi
echo ""

# Test 3: Start Conversation
echo "3. Testing Start Conversation..."
CONVERSATION_RESPONSE=$(curl -s -X POST $API_URL/api/v1/conversations/start \
    -H "Content-Type: application/json" \
    -d '{
        "scenario_type": "ECOMMERCE",
        "user_id": "test-user-'$(date +%s)'",
        "title": "Test E-commerce Support"
    }')

if [[ $CONVERSATION_RESPONSE == *"id"* ]]; then
    echo -e "${GREEN}✓ Conversation created successfully${NC}"
    # Extract conversation ID using grep and sed
    CONV_ID=$(echo $CONVERSATION_RESPONSE | grep -o '"id":"[^"]*' | sed 's/"id":"//')
    echo "   Conversation ID: $CONV_ID"
else
    echo -e "${RED}✗ Failed to create conversation${NC}"
    echo "   Response: $CONVERSATION_RESPONSE"
    CONV_ID=""
fi
echo ""

# Test 4: Send Message (if conversation was created)
if [[ ! -z "$CONV_ID" ]]; then
    echo "4. Testing Send Message..."
    MESSAGE_RESPONSE=$(curl -s -X POST $API_URL/api/v1/conversations/$CONV_ID/messages \
        -H "Content-Type: application/json" \
        -d '{
            "role": "USER",
            "content": "I need help with my order",
            "conversation_id": 1
        }')
    
    if [[ $MESSAGE_RESPONSE == *"content"* ]]; then
        echo -e "${GREEN}✓ Message sent successfully${NC}"
        MESSAGE_ID=$(echo $MESSAGE_RESPONSE | grep -o '"id":[0-9]*' | sed 's/"id"://')
        echo "   Message ID: $MESSAGE_ID"
    else
        echo -e "${RED}✗ Failed to send message${NC}"
        echo "   Response: $MESSAGE_RESPONSE"
    fi
    echo ""
    
    # Test 5: Get Messages
    echo "5. Testing Get Messages..."
    MESSAGES_RESPONSE=$(curl -s $API_URL/api/v1/conversations/$CONV_ID/messages)
    if [[ $MESSAGES_RESPONSE == *"["* ]]; then
        echo -e "${GREEN}✓ Messages retrieved successfully${NC}"
        MESSAGE_COUNT=$(echo $MESSAGES_RESPONSE | grep -o '"id"' | wc -l)
        echo "   Total messages: $MESSAGE_COUNT"
    else
        echo -e "${RED}✗ Failed to retrieve messages${NC}"
    fi
    echo ""
    
    # Test 6: Get Conversation Details
    echo "6. Testing Get Conversation Details..."
    CONV_DETAILS=$(curl -s $API_URL/api/v1/conversations/$CONV_ID)
    if [[ $CONV_DETAILS == *"scenario_type"* ]]; then
        echo -e "${GREEN}✓ Conversation details retrieved${NC}"
    else
        echo -e "${RED}✗ Failed to retrieve conversation details${NC}"
    fi
    echo ""
fi

# Test 7: List Conversations
echo "7. Testing List Conversations..."
LIST_RESPONSE=$(curl -s "$API_URL/api/v1/conversations/?limit=5")
if [[ $LIST_RESPONSE == *"["* ]]; then
    echo -e "${GREEN}✓ Conversations list retrieved${NC}"
    CONV_COUNT=$(echo $LIST_RESPONSE | grep -o '"id"' | wc -l)
    echo "   Conversations found: $CONV_COUNT"
else
    echo -e "${RED}✗ Failed to list conversations${NC}"
fi
echo ""

# Test 8: Test Different Scenarios
echo "8. Testing Different Scenario Types..."
SCENARIOS=("ECOMMERCE" "SAAS" "SERVICE_BUSINESS")
for SCENARIO in "${SCENARIOS[@]}"; do
    SCENARIO_RESPONSE=$(curl -s -X POST $API_URL/api/v1/conversations/start \
        -H "Content-Type: application/json" \
        -d '{
            "scenario_type": "'$SCENARIO'",
            "user_id": "test-'$SCENARIO'-user",
            "title": "Test '$SCENARIO' Scenario"
        }')
    
    if [[ $SCENARIO_RESPONSE == *"id"* ]]; then
        echo -e "${GREEN}✓ $SCENARIO scenario: OK${NC}"
    else
        echo -e "${RED}✗ $SCENARIO scenario: FAILED${NC}"
    fi
done
echo ""

echo "======================================"
echo "API Test Suite Complete!"
echo "======================================"
echo ""
echo "Test Summary:"
echo "- Backend API: $API_URL"
echo "- All endpoints tested"
echo "- Check logs for any errors: docker logs biwoco-backend-final"
echo ""