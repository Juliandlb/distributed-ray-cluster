#!/bin/bash

# Simple deployment script for Docker Swarm Ray Cluster

set -e

echo "🚀 Deploying Ray Cluster to Docker Swarm"
echo "========================================"

# Check if Docker Swarm is initialized
if ! docker info | grep -q "Swarm: active"; then
    echo "🔧 Initializing Docker Swarm..."
    docker swarm init
fi

# Remove existing stack if it exists
echo "🧹 Removing existing stack..."
docker stack rm ray-cluster 2>/dev/null || true

# Wait for stack removal to complete
echo "⏳ Waiting for stack removal to complete..."
sleep 10

# Deploy the stack
echo "📦 Deploying new stack..."
docker stack deploy -c docker-swarm.yml ray-cluster

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Check service status
echo "📊 Checking service status..."
docker stack services ray-cluster

echo ""
echo "🔍 Monitoring service startup..."
echo "Press Ctrl+C to stop monitoring"

# Monitor services until they're all running
while true; do
    echo ""
    echo "📊 Current status:"
    docker stack services ray-cluster
    
    # Check if all services are running
    if docker stack services ray-cluster | grep -q "0/"; then
        echo "⏳ Some services still starting..."
        sleep 10
    else
        echo ""
        echo "✅ All services are running!"
        break
    fi
done

echo ""
echo "🎉 Cluster deployed successfully!"
echo ""
echo "📋 Useful commands:"
echo "   Check status: docker stack services ray-cluster"
echo "   View logs: docker service logs ray-cluster_ray-head"
echo "   Scale workers: docker service scale ray-cluster_ray-worker=3"
echo "   Run demo: docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest"
echo ""
echo "🔗 Ray Dashboard: http://localhost:8265" 