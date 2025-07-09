#!/bin/bash
set -e

# Check if head IP is provided
if [ $# -eq 0 ]; then
    echo "❌ Error: Head node IP address is required"
    echo "Usage: $0 <HEAD_NODE_IP>"
    echo "Example: $0 192.168.1.100"
    exit 1
fi

HEAD_IP=$1
WORKER_IP=$(hostname -I | awk '{print $1}')

echo "🤖 Starting Standalone Ray Worker"
echo "================================"
echo "📍 Worker IP: $WORKER_IP"
echo "🔗 Connecting to Head: $HEAD_IP:6379"

# Build the worker image
echo "🔨 Building worker image..."
docker build -f Dockerfile.worker -t ray-cluster-worker:latest .

# Create a standalone worker container
echo "🚀 Starting standalone worker container..."
docker run -d \
    --name ray-standalone-worker \
    --env RAY_HEAD_ADDRESS=$HEAD_IP:6379 \
    --env RAY_DISABLE_DEDUP=1 \
    --env RAY_DISABLE_CUSTOM_LOGGER=1 \
    --env PYTHONUNBUFFERED=1 \
    --env RAY_memory_usage_threshold=0.9 \
    --env RAY_memory_monitor_refresh_ms=2000 \
    --env RAY_object_spilling_config='{"type":"filesystem","params":{"directory_path":"/tmp/ray/spill"}}' \
    --env RAY_raylet_start_wait_time_s=60 \
    --env RAY_gcs_server_port=6379 \
    --env RAY_redis_port=6379 \
    --env RAY_object_manager_port=12345 \
    --env RAY_node_manager_port=12346 \
    --env RAY_redis_password= \
    --env RAY_redis_db=0 \
    --env RAY_redis_max_memory=1000000000 \
    --env RAY_redis_max_memory_policy=allkeys-lru \
    --memory=3g \
    --cpus=2.0 \
    --restart=unless-stopped \
    ray-cluster-worker:latest

echo ""
echo "✅ Standalone worker started!"
echo "============================"
echo "📍 Worker IP: $WORKER_IP"
echo "🔗 Connected to: $HEAD_IP:6379"
echo ""
echo "📊 Check worker status:"
echo "   docker logs ray-standalone-worker"
echo ""
echo "🎮 Test the cluster from head node:"
echo "   docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest"
echo ""
echo "🛑 To stop the worker:"
echo "   docker stop ray-standalone-worker" 