#!/bin/bash
set -e

echo "=== Starting Ray Worker Node ==="
echo "Node ID: $(hostname)"
echo "IP Address: $(hostname -i)"
echo "Head Address: ${RAY_HEAD_ADDRESS}"

# Validate required environment variables
if [ -z "$RAY_HEAD_ADDRESS" ]; then
    echo "ERROR: RAY_HEAD_ADDRESS environment variable is required"
    exit 1
fi

# Create necessary directories
mkdir -p /tmp/ray /tmp/ray/spill /app/logs

# Wait for head node to be ready with improved retry logic
echo "Waiting for head node to be ready..."
retry_count=0
max_retries=60  # Increased retries
retry_interval=10

# Extract host and port from RAY_HEAD_ADDRESS
head_host=$(echo $RAY_HEAD_ADDRESS | cut -d: -f1)
head_port=$(echo $RAY_HEAD_ADDRESS | cut -d: -f2)

echo "Testing connection to $head_host:$head_port..."

while [ $retry_count -lt $max_retries ]; do
    if nc -z $head_host $head_port; then
        echo "✅ Head node is ready!"
        break
    else
        echo "Attempt $((retry_count + 1))/$max_retries: Head node not ready, waiting ${retry_interval}s..."
        sleep $retry_interval
        retry_count=$((retry_count + 1))
        
        # Increase wait time progressively
        if [ $retry_count -gt 10 ]; then
            retry_interval=20
        fi
        if [ $retry_count -gt 20 ]; then
            retry_interval=30
        fi
    fi
done

if [ $retry_count -eq $max_retries ]; then
    echo "ERROR: Failed to connect to head node after $max_retries attempts"
    echo "This may indicate the head node is not running or there are network issues"
    exit 1
fi

# Additional wait to ensure Ray services are fully ready
echo "Waiting additional 10 seconds for Ray services to be fully ready..."
sleep 10

# Determine GPU configuration
if [ -n "$CUDA_VISIBLE_DEVICES" ]; then
    echo "GPU devices: $CUDA_VISIBLE_DEVICES"
    gpu_arg="--num-gpus=$(echo $CUDA_VISIBLE_DEVICES | tr ',' '\n' | wc -l)"
else
    echo "No GPU devices specified"
    gpu_arg=""
fi

# Join the cluster with improved configuration
echo "Joining Ray cluster at $RAY_HEAD_ADDRESS..."
ray start --address=$RAY_HEAD_ADDRESS \
    --object-store-memory=800000000 \
    --num-cpus=2 \
    $gpu_arg \
    --temp-dir=/tmp/ray

echo "✅ Ray worker node joined successfully!"

# Additional wait to ensure Ray is fully initialized
echo "Waiting 5 seconds for Ray to fully initialize..."
sleep 5

# Start the main application in worker mode
echo "Starting main application in worker mode..."
python /app/main.py --mode=worker --config=/app/config/laptop_config.yaml 