#!/bin/bash

# One-command rebuild and redeploy script
# This script cleans up, rebuilds, and redeploys the entire cluster

set -e

echo "🔄 Complete Rebuild and Redeploy"
echo "================================"

# Step 1: Cleanup
echo "🧹 Step 1: Cleaning up..."
./cleanup.sh

# Step 2: Build images
echo ""
echo "🔨 Step 2: Building images..."
./build-swarm.sh

# Step 3: Deploy cluster
echo ""
echo "🚀 Step 3: Deploying cluster..."
./deploy-swarm.sh

echo ""
echo "🎉 Rebuild and deploy completed!"
echo ""
echo "🎮 To run the demo:"
echo "   docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest" 