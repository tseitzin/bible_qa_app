#!/bin/bash

# Performance testing script for Bible Q&A API

echo "======================================"
echo "Bible Q&A API Performance Test"
echo "======================================"
echo ""

# Test questions
declare -a questions=(
    "Who is Jesus?"
    "What is faith?"
    "What does the Bible say about love?"
)

# Function to test a question
test_question() {
    local question=$1
    local start_time=$(date +%s.%N)
    
    response=$(curl -s -X POST http://localhost:8000/api/ask \
        -H "Content-Type: application/json" \
        -d "{\"question\": \"$question\"}")
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    echo "$duration"
}

# Run tests
for question in "${questions[@]}"; do
    echo "Testing: $question"
    total=0
    runs=3
    
    for i in $(seq 1 $runs); do
        duration=$(test_question "$question")
        echo "  Run $i: ${duration}s"
        total=$(echo "$total + $duration" | bc)
    done
    
    avg=$(echo "scale=2; $total / $runs" | bc)
    echo "  Average: ${avg}s"
    echo ""
done

echo "======================================"
echo "Test Complete"
echo "======================================"
