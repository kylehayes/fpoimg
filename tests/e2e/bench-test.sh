#!/bin/bash
# FPOImg Comprehensive Test using curl
# Tests 200 different image permutations at max 5 RPS

# Configuration
BASE_URL="https://staging-dot-fpoimg.wl.r.appspot.com"
TOTAL_REQUESTS=200
MAX_RPS=5

# Create URL permutation arrays
DIMENSIONS=(
    "100x100" "200x200" "300x300" "400x400" "500x500"
    "300x250" "336x280" "728x90" "160x600" "970x250"
    "320x50" "120x600" "468x60" "300x600" "250x250"
)

BG_COLORS=(
    "ff0000" "00ff00" "0000ff" "ffff00" "ff00ff"
    "00ffff" "000000" "ffffff" "808080" "ffa500"
)

TEXT_COLORS=(
    "ffffff" "000000" "ff0000" "00ff00" "0000ff"
)

TEXTS=(
    "Sample" "Preview" "Test" "Placeholder" "Demo"
)

echo "==== FPOImg Permutation Test ===="
echo "Base URL: $BASE_URL"
echo "Testing $TOTAL_REQUESTS permutations at max $MAX_RPS RPS"
echo ""

# Initialize counters
total_requests=0
total_success=0
total_failed=0
total_time=0
min_time=9999
max_time=0

# Start time for rate limiting
start_batch_time=$(date +%s)
requests_in_current_second=0

# Run tests
for ((i=1; i<=TOTAL_REQUESTS; i++)); do
    # Get random elements from arrays
    dim=${DIMENSIONS[$((RANDOM % ${#DIMENSIONS[@]}))]}
    bg=${BG_COLORS[$((RANDOM % ${#BG_COLORS[@]}))]}
    txt=${TEXT_COLORS[$((RANDOM % ${#TEXT_COLORS[@]}))]}
    text=${TEXTS[$((RANDOM % ${#TEXTS[@]}))]}
    
    # Create the URL based on the patterns in your Flask app
    r=$((RANDOM % 5))
    case $r in
        0) # Just dimensions (width x height)
            url="$BASE_URL/$dim"
            ;;
        1) # Square image (single dimension)
            dim_size=${dim%%x*}  # Extract first dimension
            url="$BASE_URL/$dim_size"
            ;;
        2) # Dimensions with text via query parameter
            url="$BASE_URL/$dim?text=$text"
            ;;
        3) # Dimensions with colors via query parameters
            url="$BASE_URL/$dim?bg_color=$bg&text_color=$txt"
            ;;
        4) # Dimensions with text in path parameter
            url="$BASE_URL/$dim/$text"
            ;;
    esac
    
    # Add cache buster properly based on URL pattern
    if [[ "$url" == *"?"* ]]; then
        # URL already has query parameters, append with &
        url="${url}&cache_buster=$i"
    else
        # URL doesn't have query parameters, append with ?
        url="${url}?cache_buster=$i"
    fi
    
    # Print progress
    echo -n "[$i/$TOTAL_REQUESTS] Testing: $url ... "
    
    # Make the request with curl
    response=$(curl -s -o /dev/null -w "%{http_code} %{time_total}" "$url")
    status_code=$(echo $response | cut -d' ' -f1)
    request_time=$(echo $response | cut -d' ' -f2)
    
    # Check status code
    if [ "$status_code" == "200" ]; then
        echo "SUCCESS (${request_time}s)"
        total_success=$((total_success + 1))
        
        # Update statistics
        total_time=$(echo "$total_time + $request_time" | bc)
        
        if (( $(echo "$request_time < $min_time" | bc -l) )); then
            min_time=$request_time
        fi
        
        if (( $(echo "$request_time > $max_time" | bc -l) )); then
            max_time=$request_time
        fi
    else
        echo "FAILED ($status_code)"
        total_failed=$((total_failed + 1))
    fi
    
    total_requests=$((total_requests + 1))
    requests_in_current_second=$((requests_in_current_second + 1))
    
    # Rate limiting
    current_time=$(date +%s)
    elapsed=$((current_time - start_batch_time))
    
    if [ $elapsed -eq 0 ]; then
        # If we're still in the same second and reached our RPS limit, sleep
        if [ $requests_in_current_second -ge $MAX_RPS ]; then
            echo "Rate limiting: waiting for next second"
            sleep 1
            requests_in_current_second=0
            start_batch_time=$(date +%s)
        fi
    else
        # If we've moved to a new second, reset counter
        requests_in_current_second=0
        start_batch_time=$current_time
    fi
done

# Calculate statistics
if [ $total_success -gt 0 ]; then
    avg_time=$(echo "scale=3; $total_time / $total_success" | bc)
else
    avg_time="N/A"
    min_time="N/A"
    max_time="N/A"
fi
success_rate=$(echo "scale=1; 100 * $total_success / $total_requests" | bc)

echo ""
echo "==== Test Results ===="
echo "Total URLs Tested: $total_requests"
echo "Successful: $total_success"
echo "Failed: $total_failed"
echo "Success Rate: ${success_rate}%"
echo "Average Response Time: ${avg_time}s"
echo "Min Response Time: ${min_time}s"
echo "Max Response Time: ${max_time}s"

echo "Test completed."