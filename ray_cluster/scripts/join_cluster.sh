#!/bin/bash

# Script to join a Ray cluster from any machine
# Usage: ./join_cluster.sh <head-node-ip> [gpu-devices]

set -e

HEAD_NODE_IP=${1:-"localhost"}
GPU_DEVICES=${2:-"0"}
CONTAINER_NAME="ray-worker-$(hostname)-$(date +%s)"

echo "=== Joining Ray Cluster ==="
echo "Head Node: $HEAD_NODE_IP"
echo "GPU Devices: $GPU_DEVICES"
echo "Container Name: $CONTAINER_NAME"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running"
    exit 1
fi

# Check if we can reach the head node
echo "Testing connection to head node..."
if ! nc -z $HEAD_NODE_IP 6379; then
    echo "ERROR: Cannot connect to head node at $HEAD_NODE_IP:6379"
    echo "Please ensure the head node is running and accessible"
    exit 1
fi

echo "Connection successful!"

# Pull the worker image if not available locally
if ! docker image inspect ray-cluster-worker:latest > /dev/null 2>&1; then
    echo "Worker image not found locally. Please build it first:"
    echo "  docker build -f Dockerfile.worker -t ray-cluster-worker:latest ."
    exit 1
fi

# Start the worker container
echo "Starting worker container..."
docker run -d \
    --name $CONTAINER_NAME \
    --network host \
    -e RAY_HEAD_ADDRESS=$HEAD_NODE_IP:6379 \
    -e CUDA_VISIBLE_DEVICES=$GPU_DEVICES \
    -e RAY_DISABLE_DEDUP=1 \
    -e RAY_DISABLE_CUSTOM_LOGGER=1 \
    -e PYTHONUNBUFFERED=1 \
    -v /tmp/ray:/tmp/ray \
    ray-cluster-worker:latest

echo "Worker container started successfully!"
echo "Container ID: $CONTAINER_NAME"
echo ""
echo "To view logs:"
echo "  docker logs -f $CONTAINER_NAME"
echo ""
echo "To stop the worker:"
echo "  docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME"
echo ""
echo "To check cluster status, visit the Ray dashboard:"
echo "  http://$HEAD_NODE_IP:8265" 