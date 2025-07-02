#!/bin/bash

# Cleanup script for Ray Cluster

echo "🧹 Cleaning up Ray Cluster"
echo "=========================="

# Remove Docker Swarm stack
echo "🗑️  Removing Docker Swarm stack..."
docker stack rm ray-cluster 2>/dev/null || true

# Wait for stack removal
echo "⏳ Waiting for stack removal..."
sleep 10

# Stop and remove old laptop containers
echo "🧹 Cleaning up old containers..."
docker stop ray-cluster-head-laptop ray-cluster-worker-laptop 2>/dev/null || true
docker rm ray-cluster-head-laptop ray-cluster-worker-laptop 2>/dev/null || true

# Remove images (optional - uncomment if you want to remove images too)
# echo "🗑️  Removing images..."
# docker rmi ray-cluster-head:latest ray-cluster-worker:latest ray-cluster-client:latest 2>/dev/null || true

# Clean up any dangling containers
echo "🧹 Cleaning up dangling containers..."
docker container prune -f

echo ""
echo "✅ Cleanup completed!"
echo ""
echo "To rebuild and redeploy:"
echo "   ./build-swarm.sh"
echo "   ./deploy-swarm.sh" 