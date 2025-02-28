#!/bin/bash
# Simple FPOImg Load Test using curl
# This script tests if your FPOImg service can handle 5 requests per second

# Configuration
STAGING_URL="https://staging-dot-fpoimg.wl.r.appspot.com"
PRODUCTION_URL="https://fpoimg.wl.r.appspot.com"

# Function to run a simple load test
run_load_test() {
  local ENV_NAME=$1
  local BASE_URL=$2
  local REQUESTS=$3  # Number of requests to make
  local RATE=$4      # Requests per second
  
  echo ""
  echo "========================================"
  echo "Testing $ENV_NAME environment at $RATE RPS"
  echo "URL: $BASE_URL"
  echo "========================================"
  
  # Array of test URLs
  URLS=(
    "${BASE_URL}/300x200"
    "${BASE_URL}/400"
    "${BASE_URL}/400x300?text=Test+Image"
    "${BASE_URL}/400x300/Custom+Caption"
    "${BASE_URL}/600x400?bg_color=ff0000&text_color=ffffff"
    "${BASE_URL}/300x250?text=Preview&bg_color=e61919&text_color=ffffff"
  )
  
  # Track results
  local success_count=0
  local fail_count=0
  local total_time=0
  local max_time=0
  local min_time=999
  
  echo "Starting test: $REQUESTS requests at ~$RATE RPS..."
  start_time=$(date +%s)
  
  for ((i=1; i<=$REQUESTS; i++)); do
    # Select a URL randomly from the array
    url_index=$((RANDOM % ${#URLS[@]}))
    test_url="${URLS[$url_index]}?cache=$i"
    
    # Start background requests to maintain RPS
    if ((i % $RATE == 0)); then
      # Every batch of $RATE requests, sleep 1 second
      sleep_until=$((start_time + i/$RATE))
      current_time=$(date +%s)
      if (( $sleep_until > $current_time )); then
        sleep_duration=$(( $sleep_until - $current_time ))
        sleep $sleep_duration
      fi
    fi
    
    # Make the request and measure time
    echo -n "."
    response=$(curl -s -w "%{http_code} %{time_total}" -o /dev/null "$test_url")
    status_code=$(echo $response | cut -d' ' -f1)
    request_time=$(echo $response | cut -d' ' -f2)
    
    # Track stats
    total_time=$(echo "$total_time + $request_time" | bc)
    
    # Update min/max times
    if (( $(echo "$request_time > $max_time" | bc -l) )); then
      max_time=$request_time
    fi
    
    if (( $(echo "$request_time < $min_time" | bc -l) )); then
      min_time=$request_time
    fi
    
    if [[ $status_code == "200" ]]; then
      ((success_count++))
    else
      ((fail_count++))
      echo "F"  # Print F for failures
    fi
    
    # Show progress every 10 requests
    if ((i % 10 == 0)); then
      echo -n "$i"
    fi
  done
  
  end_time=$(date +%s)
  duration=$((end_time - start_time))
  actual_rps=$(echo "scale=2; $REQUESTS / $duration" | bc)
  avg_time=$(echo "scale=3; $total_time / $REQUESTS" | bc)
  success_rate=$(echo "scale=1; $success_count * 100 / $REQUESTS" | bc)
  
  echo ""
  echo ""
  echo "Test Results:"
  echo "-------------"
  echo "Total Requests: $REQUESTS"
  echo "Duration: $duration seconds"
  echo "Target RPS: $RATE"
  echo "Actual RPS: $actual_rps"
  echo "Success Rate: $success_rate%"
  echo "Average Response Time: ${avg_time}s"
  echo "Min Response Time: ${min_time}s"
  echo "Max Response Time: ${max_time}s"
  
  if (( $(echo "$actual_rps >= $RATE * 0.9" | bc -l) )) && (( $(echo "$success_rate >= 99" | bc -l) )); then
    echo "TEST PASSED: Service can handle $RATE RPS"
    return 0
  else
    echo "TEST FAILED: Service cannot reliably handle $RATE RPS"
    return 1
  fi
}

# Ask which environment to test
echo "FPOImg Load Test"
echo "================"
echo "This test will verify if your service can handle 5 requests per second."
echo ""
echo "Which environment would you like to test?"
echo "1) Staging"
echo "2) Production"
echo "3) Both environments"
read -p "Select an option (1-3): " TEST_OPTION

# Check for required command
if ! command -v bc &> /dev/null; then
    echo "This script requires the 'bc' command for floating point calculations."
    echo "Please install it with: sudo apt-get install bc (Ubuntu/Debian)"
    echo "or: brew install bc (macOS)"
    exit 1
fi

# Run the selected test
case $TEST_OPTION in
    1)
        run_load_test "staging" "$STAGING_URL" 50 5
        ;;
    2)
        run_load_test "production" "$PRODUCTION_URL" 50 5
        ;;
    3)
        echo ""
        echo "Testing both environments..."
        staging_result=0
        production_result=0
        
        run_load_test "staging" "$STAGING_URL" 50 5
        staging_result=$?
        
        echo ""
        echo "Now testing production..."
        echo ""
        
        run_load_test "production" "$PRODUCTION_URL" 50 5
        production_result=$?
        
        echo ""
        echo "Summary:"
        echo "--------"
        if [ $staging_result -eq 0 ]; then
            echo "Staging: PASSED"
        else
            echo "Staging: FAILED"
        fi
        
        if [ $production_result -eq 0 ]; then
            echo "Production: PASSED"
        else
            echo "Production: FAILED"
        fi
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac

echo ""
echo "Test completed."