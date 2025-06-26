#!/bin/bash

# Build script for Docker Swarm Ray Cluster
# This script builds the necessary images for the distributed Ray cluster

set -e

echo "🔨 [BUILDING] Docker Swarm Ray Cluster Images"
echo "=============================================="

# Build base image first
echo "📦 [BUILDING] Base image..."
docker build -f Dockerfile.base -t ray-cluster-base:latest .

if [ $? -eq 0 ]; then
    echo "✅ [SUCCESS] Base image built successfully"
else
    echo "❌ [ERROR] Failed to build base image"
    exit 1
fi

# Build head node image
echo "📦 [BUILDING] Head node image..."
docker build -f Dockerfile.head -t ray-cluster-head:latest .

if [ $? -eq 0 ]; then
    echo "✅ [SUCCESS] Head node image built successfully"
else
    echo "❌ [ERROR] Failed to build head node image"
    exit 1
fi

# Build worker node image
echo "📦 [BUILDING] Worker node image..."
docker build -f Dockerfile.worker -t ray-cluster-worker:latest .

if [ $? -eq 0 ]; then
    echo "✅ [SUCCESS] Worker node image built successfully"
else
    echo "❌ [ERROR] Failed to build worker node image"
    exit 1
fi

echo ""
echo "🎉 [SUCCESS] All images built successfully!"
echo "📋 [IMAGES] Available images:"
docker images | grep ray-cluster

echo ""
echo "🚀 [NEXT STEPS] To deploy the cluster:"
echo "   1. Initialize Docker Swarm: docker swarm init"
echo "   2. Deploy the stack: docker stack deploy -c docker-swarm.yml ray-cluster"
echo "   3. Check status: docker stack services ray-cluster"
echo "   4. Scale workers: docker service scale ray-cluster_ray-worker=3" 