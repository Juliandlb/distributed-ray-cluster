#!/bin/bash

# Simple build script for Docker Swarm deployment
# This script builds head and worker images directly without using a base image

set -e

echo "🔨 Building Ray Cluster Images for Docker Swarm"
echo "================================================"

# Clean up any existing containers from old setup
echo "🧹 Cleaning up old containers..."
docker stop ray-cluster-head-laptop ray-cluster-worker-laptop 2>/dev/null || true
docker rm ray-cluster-head-laptop ray-cluster-worker-laptop 2>/dev/null || true

# Remove old images to ensure clean build
echo "🗑️  Removing old images..."
docker rmi ray-cluster-head:latest ray-cluster-worker:latest ray-cluster-client:latest 2>/dev/null || true

# Build head node image
echo "🏗️  Building head node image..."
docker build -t ray-cluster-head:latest -f Dockerfile.head .

# Build worker node image
echo "🏗️  Building worker node image..."
docker build -t ray-cluster-worker:latest -f Dockerfile.worker .

# Build client image
echo "🏗️  Building client image..."
docker build -t ray-cluster-client:latest -f Dockerfile.client .

echo ""
echo "✅ All images built successfully!"
echo ""
echo "📋 Built images:"
docker images | grep ray-cluster
echo ""
echo "🚀 To deploy the cluster, run:"
echo "   ./deploy-swarm.sh"
echo ""
echo "🎮 To run the demo, run:"
echo "   docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest" 