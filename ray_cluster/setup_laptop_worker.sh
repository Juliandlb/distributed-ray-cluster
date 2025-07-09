#!/bin/bash
set -e

# Check if head IP is provided
if [ $# -eq 0 ]; then
    echo "❌ Error: Head node IP address is required"
    echo "Usage: $0 <HEAD_NODE_IP>"
    echo "Example: $0 52.224.243.185"
    exit 1
fi

HEAD_IP=$1

echo "🖥️  Setting up Laptop Ray Worker"
echo "================================"
echo "🔗 Connecting to Azure VM at: $HEAD_IP"

# Check if repository exists, if not clone it
if [ ! -d "distributed-ray-cluster" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/Juliandlb/distributed-ray-cluster.git
fi

cd distributed-ray-cluster/ray_cluster

# Make the script executable
chmod +x start_remote_worker_direct.sh

# Start the direct worker
echo "🚀 Starting direct Ray worker..."
./start_remote_worker_direct.sh $HEAD_IP

echo ""
echo "✅ Laptop worker setup complete!"
echo "🔗 Your laptop is now connected to the Azure VM Ray cluster"
echo ""
echo "📊 To check worker status:"
echo "   docker logs ray-direct-worker"
echo ""
echo "🎮 To test the cluster from your laptop:"
echo "   docker run --rm -it ray-cluster-client:latest" 