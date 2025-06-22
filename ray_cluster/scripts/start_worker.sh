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

# Wait for head node to be ready
echo "Waiting for head node to be ready..."
retry_count=0
max_retries=30
retry_interval=10

# Extract host and port from RAY_HEAD_ADDRESS
head_host=$(echo $RAY_HEAD_ADDRESS | cut -d: -f1)
head_port=$(echo $RAY_HEAD_ADDRESS | cut -d: -f2)

while [ $retry_count -lt $max_retries ]; do
    if nc -z $head_host $head_port; then
        echo "Head node is ready!"
        break
    else
        echo "Attempt $((retry_count + 1))/$max_retries: Head node not ready, waiting ${retry_interval}s..."
        sleep $retry_interval
        retry_count=$((retry_count + 1))
    fi
done

if [ $retry_count -eq $max_retries ]; then
    echo "ERROR: Failed to connect to head node after $max_retries attempts"
    exit 1
fi

# Determine GPU configuration
if [ -n "$CUDA_VISIBLE_DEVICES" ]; then
    echo "GPU devices: $CUDA_VISIBLE_DEVICES"
    gpu_arg="--num-gpus=$(echo $CUDA_VISIBLE_DEVICES | tr ',' '\n' | wc -l)"
else
    echo "No GPU devices specified"
    gpu_arg=""
fi

# Join the cluster
echo "Joining Ray cluster at $RAY_HEAD_ADDRESS..."
ray start --address=$RAY_HEAD_ADDRESS \
    --object-store-memory=500000000 \
    --num-cpus=2 \
    $gpu_arg \
    --temp-dir=/tmp/ray

echo "Ray worker node joined successfully!"

# Start the main application in worker mode
echo "Starting main application in worker mode..."
python /app/main.py --mode=worker --config=/app/worker_config.yaml 