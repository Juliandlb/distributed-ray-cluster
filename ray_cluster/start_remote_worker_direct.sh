#!/usr/bin/env bash

set -e

if [ -z "$1" ]; then
  echo "❌ Error: Head node IP address is required"
  echo "Usage: $0 <HEAD_NODE_IP>"
  echo "Example: $0 52.224.243.185"
  exit 1
fi

HEAD_NODE_IP="$1"
RAY_HEAD_ADDRESS="$HEAD_NODE_IP:6379"

# Remove any old container
if docker ps -a --format '{{.Names}}' | grep -Eq '^ray-direct-worker$'; then
  echo "🧹 Removing old ray-direct-worker container..."
  docker rm -f ray-direct-worker || true
fi

# Get worker IP (best effort, fallback to empty)
WORKER_IP=$(hostname -I 2>/dev/null | awk '{print $1}')

cat <<EOF
🤖 Starting Direct Ray Worker
============================
📍 Worker IP: $WORKER_IP
🔗 Connecting to Head: $RAY_HEAD_ADDRESS
🔨 Building worker image...
EOF

docker build -f Dockerfile.worker -t ray-cluster-worker:latest .

echo "🚀 Starting direct worker container..."
docker run --rm --network host --name ray-direct-worker \
  -e RAY_HEAD_ADDRESS="$RAY_HEAD_ADDRESS" \
  ray-cluster-worker:latest 