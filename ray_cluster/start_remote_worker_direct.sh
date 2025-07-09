#!/bin/bash
set -e

# Check if head IP is provided
if [ $# -eq 0 ]; then
    echo "❌ Error: Head node IP address is required"
    echo "Usage: $0 <HEAD_NODE_IP>"
    echo "Example: $0 52.224.243.185"
    exit 1
fi

HEAD_IP=$1
WORKER_IP=$(hostname -I | awk '{print $1}')

echo "🤖 Starting Direct Ray Worker"
echo "============================"
echo "📍 Worker IP: $WORKER_IP"
echo "🔗 Connecting to Head: $HEAD_IP:6379"

# Build the worker image
echo "🔨 Building worker image..."
docker build -f Dockerfile.worker -t ray-cluster-worker:latest .

# Create a standalone worker container that connects directly to Ray
echo "🚀 Starting direct worker container..."
docker run -d \
    --name ray-direct-worker \
    --env RAY_HEAD_ADDRESS=$HEAD_IP:6379 \
    --env RAY_DISABLE_DEDUP=1 \
    --env RAY_DISABLE_CUSTOM_LOGGER=1 \
    --env PYTHONUNBUFFERED=1 \
    ray-cluster-worker:latest

echo ""
echo "✅ Direct worker started!"
echo "🔗 Worker is connecting to Ray head at: $HEAD_IP:6379"
echo ""
echo "📊 To check worker status:"
echo "   docker logs ray-direct-worker"
echo ""
echo "🛑 To stop worker:"
echo "   docker stop ray-direct-worker && docker rm ray-direct-worker" 