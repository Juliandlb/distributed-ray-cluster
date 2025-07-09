#!/bin/bash
set -e

echo "🚀 Starting Ray Cluster (Head Node)"
echo "=================================="

# Get both private and public IP addresses
PRIVATE_IP=$(hostname -I | awk '{print $1}')
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "N/A")
echo "📍 Private IP: $PRIVATE_IP"
echo "📍 Public IP: $PUBLIC_IP"

# Check if Docker Swarm is initialized
if ! docker info | grep -q "Swarm: active"; then
    echo "🔧 Initializing Docker Swarm..."
    docker swarm init --advertise-addr $PRIVATE_IP
fi

# Get the join token for workers
JOIN_TOKEN=$(docker swarm join-token -q worker)
echo ""
echo "🎯 CLUSTER READY FOR INTERNET WORKERS!"
echo "======================================"
echo "📍 Private IP: $PRIVATE_IP"
echo "📍 Public IP: $PUBLIC_IP"
echo "🔌 Ray Port: 6379"
echo "📊 Dashboard: http://$PUBLIC_IP:8265"
echo ""
echo "🔑 Join Token: $JOIN_TOKEN"
echo ""
echo "🔗 To connect a remote worker, try these commands on the remote machine:"
echo ""
echo "   # Option 1: Same network (VPC/VPN) - use private IP"
echo "   docker swarm join --token $JOIN_TOKEN $PRIVATE_IP:2377"
echo ""
echo "   # Option 2: Different network - use public IP (requires port forwarding)"
echo "   docker swarm join --token $JOIN_TOKEN $PUBLIC_IP:2377"
echo ""
echo "After joining, scale workers from the manager (this node):"
echo "   docker service scale ray-cluster_ray-worker=<num>"
echo ""
echo "🎮 To test the cluster:"
echo "   docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest"
echo ""
echo "✅ Cluster is running and ready for remote workers!"

# Build and deploy the cluster
echo "🔨 Building and deploying Ray cluster..."
./rebuild.sh

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30 