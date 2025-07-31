#!/bin/bash
set -e

echo "🚀 Starting Ray Head Node (Direct Connection)"
echo "=========================================="

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)

echo "📍 Public IP: $PUBLIC_IP"

# Start Ray head node
ray start --head --port=6379 --ray-client-server-port=10001 --dashboard-host=0.0.0.0 --dashboard-port=8265

echo ""
echo "🎯 CLUSTER READY FOR REMOTE WORKERS!"
echo "======================================"
echo "📍 Public IP: $PUBLIC_IP"
echo "🔌 Ray Port: 6379"
echo "📊 Dashboard: http://$PUBLIC_IP:8265"
echo "🔌 Ray Client Port: 10001"
echo ""
echo "✅ Head node is running!"