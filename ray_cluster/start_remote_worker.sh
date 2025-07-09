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

echo "🤖 Starting Remote Ray Worker"
echo "============================"
echo "📍 Worker IP: $WORKER_IP"
echo "🔗 Connecting to Head: $HEAD_IP:6379"

# Check if Docker Swarm is initialized
if ! docker info | grep -q "Swarm: active"; then
    echo "🔧 Initializing Docker Swarm..."
    docker swarm init --advertise-addr $WORKER_IP
fi

# Check if we're already part of the swarm
if ! docker node ls | grep -q "$(hostname)"; then
    echo "❌ Error: This node is not part of the Docker Swarm"
    echo "Please join the swarm first by running the join command from the head node"
    echo "Example: docker swarm join --token <TOKEN> $HEAD_IP:2377"
    exit 1
fi

# Build the worker image
echo "🔨 Building worker image..."
docker build -f Dockerfile.worker -t ray-cluster-worker:latest .

# Create a simple worker service
echo "🚀 Starting remote worker service..."
docker service create \
    --name ray-remote-worker \
    --image ray-cluster-worker:latest \
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
    --mount type=volume,source=ray-models,destination=/app/models \
    --mount type=volume,source=ray-worker-data,destination=/tmp/ray \
    --network ray-cluster_ray-cluster \
    --replicas 1 \
    --constraint "node.hostname==$(hostname)" \
    --restart-condition on-failure \
    --restart-delay 5s \
    --restart-max-attempts 3 \
    --restart-window 120s \
    --limit-memory 3G \
    --limit-cpus 2.0 \
    --reserve-memory 1.5G \
    --reserve-cpus 1.0 \
    ray-cluster-worker:latest

echo ""
echo "✅ Remote worker started!"
echo "========================"
echo "📍 Worker IP: $WORKER_IP"
echo "🔗 Connected to: $HEAD_IP:6379"
echo ""
echo "📊 Check worker status:"
echo "   docker service logs ray-remote-worker"
echo ""
echo "🎮 Test the cluster from head node:"
echo "   docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest" 