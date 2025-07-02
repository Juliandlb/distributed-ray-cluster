#!/bin/bash
set -e

echo "=== Starting Ray Head Node ==="
echo "Node ID: $(hostname)"
echo "IP Address: $(hostname -i)"
echo "Port: 6379"
echo "Dashboard Port: 8265"

# Create necessary directories
mkdir -p /tmp/ray /app/logs

# Start Ray head node
echo "Starting Ray head process..."
ray start --head \
    --port=6379 \
    --dashboard-port=8265 \
    --ray-client-server-port=10001 \
    --object-store-memory=500000000 \
    --num-cpus=1 \
    --temp-dir=/tmp/ray

echo "Ray head node started successfully!"
echo "Dashboard available at: http://$(hostname -i):8265"

# Start the main application in head mode
echo "Starting main application in head mode..."
python /app/main.py --mode=head --config=/app/config/laptop_config.yaml 