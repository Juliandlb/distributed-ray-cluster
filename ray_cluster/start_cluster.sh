#!/bin/bash
set -e

echo "🚀 Starting Ray Cluster (Head Node)"
echo "=================================="

# Get the machine's IP address
HEAD_IP=$(hostname -I | awk '{print $1}')
echo "📍 Head Node IP: $HEAD_IP"

# Check if Docker Swarm is initialized
if ! docker info | grep -q "Swarm: active"; then
    echo "🔧 Initializing Docker Swarm..."
    docker swarm init --advertise-addr $HEAD_IP
fi

# Build and deploy the cluster
echo "🔨 Building and deploying Ray cluster..."
./rebuild.sh

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Get the connection information
echo ""
echo "🎯 CLUSTER READY!"
echo "=================="
echo "📍 Head Node IP: $HEAD_IP"
echo "🔌 Ray Port: 6379"
echo "📊 Dashboard: http://$HEAD_IP:8265"
echo ""
echo "🔗 To connect a remote worker, run:"
echo "   ./start_remote_worker.sh $HEAD_IP"
echo ""
echo "🎮 To test the cluster:"
echo "   docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest"
echo ""
echo "✅ Cluster is running and ready for remote workers!" 