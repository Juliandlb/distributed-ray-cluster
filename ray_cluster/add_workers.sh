#!/bin/bash

# Script to add multiple worker nodes to the Ray cluster
# Usage: ./add_workers.sh <number_of_workers>

NUM_WORKERS=${1:-3}
HEAD_ADDRESS="ray-cluster-head-laptop:6379"

echo "🚀 Adding $NUM_WORKERS worker nodes to Ray cluster..."

for i in $(seq 1 $NUM_WORKERS); do
    WORKER_NAME="ray-cluster-worker-$i"
    
    # Check if container already exists
    if docker ps -a --format "table {{.Names}}" | grep -q "^$WORKER_NAME$"; then
        echo "⚠️  Container $WORKER_NAME already exists, skipping..."
        continue
    fi
    
    echo "📦 Creating worker node $i: $WORKER_NAME"
    
    docker run -d --name "$WORKER_NAME" \
        --network ray_cluster_ray-cluster \
        -e RAY_HEAD_ADDRESS="$HEAD_ADDRESS" \
        -e CUDA_VISIBLE_DEVICES= \
        -e RAY_DISABLE_DEDUP=1 \
        -e RAY_DISABLE_CUSTOM_LOGGER=1 \
        -e PYTHONUNBUFFERED=1 \
        ray_cluster-ray-worker-1
    
    if [ $? -eq 0 ]; then
        echo "✅ Worker $i started successfully"
    else
        echo "❌ Failed to start worker $i"
    fi
    
    # Small delay between workers
    sleep 2
done

echo "🎉 Added $NUM_WORKERS worker nodes!"
echo "📊 Check cluster status with: docker logs ray-cluster-head-laptop --tail 5" 