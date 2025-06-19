#!/bin/bash

echo "=== Starting Ray Cluster (Laptop Mode) ==="
echo "This configuration is optimized for limited resources:"
echo "- Memory: 2GB per container"
echo "- CPU: 2 cores per container"
echo "- Models: Only tiny-gpt2 (smallest model)"
echo ""

# Check available memory
TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')

echo "System Memory: ${TOTAL_MEM}MB total, ${AVAILABLE_MEM}MB available"

if [ $AVAILABLE_MEM -lt 3000 ]; then
    echo "⚠️  Warning: Less than 3GB available memory"
    echo "   The cluster may run slowly or fail to start"
    echo "   Consider closing other applications"
    echo ""
fi

# Build images if needed
echo "Building Docker images..."
docker build -f Dockerfile.base -t ray-cluster-base:latest . || {
    echo "❌ Failed to build base image"
    exit 1
}

docker build -f Dockerfile.head -t ray-cluster-head:latest . || {
    echo "❌ Failed to build head image"
    exit 1
}

docker build -f Dockerfile.worker -t ray-cluster-worker:latest . || {
    echo "❌ Failed to build worker image"
    exit 1
}

echo "✅ Images built successfully"

# Start the cluster with laptop configuration
echo "Starting Ray cluster with laptop configuration..."
docker-compose -f docker-compose.laptop.yml up -d

echo ""
echo "✅ Ray cluster started!"
echo ""
echo "📊 Monitor the cluster:"
echo "   Dashboard: http://localhost:8265"
echo "   Logs: docker-compose -f docker-compose.laptop.yml logs -f"
echo ""
echo "🛑 To stop the cluster:"
echo "   docker-compose -f docker-compose.laptop.yml down"
echo ""
echo "📝 Tips for laptop usage:"
echo "   - Close other applications to free up memory"
echo "   - The cluster uses ~4GB total memory"
echo "   - Only tiny-gpt2 model is loaded (fastest)"
echo "   - Monitor system resources with 'htop' or 'top'" 