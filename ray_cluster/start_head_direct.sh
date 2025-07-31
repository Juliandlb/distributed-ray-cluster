#!/bin/bash
set -e

echo "🚀 Starting Ray Head Node (Direct Connection)"
echo "=========================================="

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)

echo "📍 Public IP: $PUBLIC_IP"

# Set PYTHONPATH
export PYTHONPATH=/mnt/data/distributed-ray-cluster/ray_cluster/ray_demo_env/lib/python3.11/site-packages

# Start Ray head node
/mnt/data/distributed-ray-cluster/ray_cluster/ray_demo_env/bin/python3.11 -m ray.scripts.scripts start --head --port=6379 --ray-client-server-port=10001 --dashboard-host=0.0.0.0 --dashboard-port=8265 --temp-dir=./tmp

echo ""
echo "🎯 CLUSTER READY FOR REMOTE WORKERS!"
echo "======================================"
echo "📍 Public IP: $PUBLIC_IP"
echo "🔌 Ray Port: 6379"
echo "📊 Dashboard: http://$PUBLIC_IP:8265"
echo "🔌 Ray Client Port: 10001"
echo ""
echo "✅ Head node is running!"