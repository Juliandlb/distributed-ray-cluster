#!/bin/bash

# Script to join a worker node to the Docker Swarm Ray cluster
# This script should be run on machines that will act as worker nodes

set -e

echo "🤖 [JOINING] Worker Node to Docker Swarm Ray Cluster"
echo "===================================================="

# Configuration
MANAGER_IP="${1:-}"
WORKER_IMAGES="${2:-ray-cluster-worker:latest}"

if [ -z "$MANAGER_IP" ]; then
    echo "❌ [ERROR] Manager IP address is required"
    echo "Usage: $0 <manager_ip> [worker_image]"
    echo ""
    echo "Example:"
    echo "  $0 192.168.1.100"
    echo "  $0 192.168.1.100 ray-cluster-worker:latest"
    exit 1
fi

echo "🎯 [CONFIG] Manager IP: $MANAGER_IP"
echo "📦 [CONFIG] Worker Image: $WORKER_IMAGES"

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "❌ [ERROR] Docker is not running"
        echo "   Please start Docker and try again"
        exit 1
    fi
    echo "✅ [CHECK] Docker is running"
}

# Function to check if already in swarm
check_swarm() {
    if docker info | grep -q "Swarm: active"; then
        echo "⚠️  [WARNING] This node is already part of a swarm"
        read -p "   Do you want to leave the current swarm? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🔄 [LEAVING] Current swarm..."
            docker swarm leave --force
            echo "✅ [SUCCESS] Left current swarm"
        else
            echo "❌ [CANCELLED] Operation cancelled"
            exit 1
        fi
    fi
}

# Function to join the swarm
join_swarm() {
    echo "🔗 [JOINING] Swarm at $MANAGER_IP..."
    
    # Get join token from manager
    echo "📋 [GETTING] Join token from manager..."
    JOIN_TOKEN=$(ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$MANAGER_IP" \
        "docker swarm join-token -q worker" 2>/dev/null || echo "")
    
    if [ -z "$JOIN_TOKEN" ]; then
        echo "❌ [ERROR] Could not get join token from manager"
        echo "   Please ensure:"
        echo "   1. SSH access to manager node ($MANAGER_IP)"
        echo "   2. Docker Swarm is initialized on manager"
        echo "   3. SSH key-based authentication is set up"
        exit 1
    fi
    
    echo "🔑 [TOKEN] Join token received"
    
    # Join the swarm
    docker swarm join --token "$JOIN_TOKEN" "$MANAGER_IP:2377"
    
    if [ $? -eq 0 ]; then
        echo "✅ [SUCCESS] Successfully joined swarm"
    else
        echo "❌ [ERROR] Failed to join swarm"
        exit 1
    fi
}

# Function to pull worker image
pull_image() {
    echo "📦 [PULLING] Worker image: $WORKER_IMAGES"
    
    # Try to pull from manager's registry or Docker Hub
    if ! docker pull "$WORKER_IMAGES" 2>/dev/null; then
        echo "⚠️  [WARNING] Could not pull image from registry"
        echo "   Please ensure the image is available on this node"
        echo "   You can build it locally or copy from manager"
    else
        echo "✅ [SUCCESS] Worker image pulled successfully"
    fi
}

# Function to label the node
label_node() {
    echo "🏷️  [LABELING] Node with worker labels..."
    
    # Get current node ID
    NODE_ID=$(docker info --format '{{.Swarm.NodeID}}')
    
    if [ -n "$NODE_ID" ]; then
        # Add labels for placement constraints
        docker node update --label-add role=worker "$NODE_ID"
        docker node update --label-add zone=worker-$(hostname) "$NODE_ID"
        echo "✅ [SUCCESS] Node labeled as worker"
    else
        echo "⚠️  [WARNING] Could not get node ID for labeling"
    fi
}

# Function to show node status
show_status() {
    echo ""
    echo "📊 [NODE STATUS]"
    echo "================"
    
    echo "🖥️  [NODE INFO]"
    docker node ls
    
    echo ""
    echo "🏷️  [NODE LABELS]"
    docker node inspect self --format '{{range $k, $v := .Spec.Labels}}{{$k}}={{$v}}{{"\n"}}{{end}}'
    
    echo ""
    echo "📦 [AVAILABLE IMAGES]"
    docker images | grep ray-cluster || echo "   No ray-cluster images found"
}

# Function to create worker service
create_worker_service() {
    echo "🤖 [CREATING] Worker service..."
    
    # Create a simple worker service for this node
    cat > /tmp/worker-service.yml << EOF
version: '3.8'
services:
  ray-worker-local:
    image: $WORKER_IMAGES
    environment:
      - RAY_HEAD_ADDRESS=ray-head:6379
      - CUDA_VISIBLE_DEVICES=
      - RAY_DISABLE_DEDUP=1
      - RAY_DISABLE_CUSTOM_LOGGER=1
      - PYTHONUNBUFFERED=1
    volumes:
      - ray-models:/app/models
    networks:
      - ray-cluster
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.id == $(docker info --format '{{.Swarm.NodeID}}')
      resources:
        limits:
          memory: 3G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
    healthcheck:
      test: ["CMD", "/app/health_check.sh"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  ray-models:
    external: true

networks:
  ray-cluster:
    external: true
EOF

    echo "📋 [CREATED] Worker service configuration"
    echo "   To deploy: docker stack deploy -c /tmp/worker-service.yml ray-worker-local"
}

# Main execution
echo "🔍 [CHECKING] Prerequisites..."

check_docker
check_swarm
join_swarm
pull_image
label_node
show_status
create_worker_service

echo ""
echo "🎉 [SUCCESS] Worker node setup complete!"
echo ""
echo "📋 [NEXT STEPS]"
echo "   1. The manager can now scale the ray-worker service to include this node"
echo "   2. Check node status: docker node ls"
echo "   3. View node details: docker node inspect self"
echo ""
echo "🛠️  [MANAGEMENT]"
echo "   On manager node, scale workers: docker service scale ray-cluster_ray-worker=3"
echo "   Check service status: docker service ls"
echo "   View service logs: docker service logs ray-cluster_ray-worker" 