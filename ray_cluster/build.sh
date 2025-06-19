#!/bin/bash
set -e

echo "=== Building Ray Cluster Docker Images ==="

# Build base image first
echo "Building base image..."
docker build -f Dockerfile.base -t ray-cluster-base:latest .

# Build head node image
echo "Building head node image..."
docker build -f Dockerfile.head -t ray-cluster-head:latest .

# Build worker node image
echo "Building worker node image..."
docker build -f Dockerfile.worker -t ray-cluster-worker:latest .

echo "=== Build Complete ==="
echo "Available images:"
echo "  - ray-cluster-base:latest"
echo "  - ray-cluster-head:latest"
echo "  - ray-cluster-worker:latest"
echo ""
echo "To start the cluster:"
echo "  docker-compose up -d"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the cluster:"
echo "  docker-compose down" 