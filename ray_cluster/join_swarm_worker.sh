#!/bin/bash

# Join Docker Swarm Worker Script for Laptop
# This script joins your laptop to the Azure VM's Docker Swarm cluster

set -e

echo "🤖 Joining Docker Swarm Cluster"
echo "==============================="

# Azure VM Public IP and Join Token
MANAGER_IP="52.224.243.185"
JOIN_TOKEN="SWMTKN-1-5sq0w766njqp6c6eg6kmswle36v870v1zswr82vv2tvzk88cih-5ib29em2adeov0g8206feyxp1"

echo "📍 Manager IP: $MANAGER_IP"
echo "🔑 Join Token: $JOIN_TOKEN"
echo ""

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt update && sudo apt install docker.io"
    echo "  sudo systemctl start docker"
    echo "  sudo systemctl enable docker"
    echo "  sudo usermod -aG docker \$USER"
    echo ""
    echo "Arch Linux:"
    echo "  sudo pacman -S docker"
    echo "  sudo systemctl start docker"
    echo "  sudo systemctl enable docker"
    echo "  sudo usermod -aG docker \$USER"
    echo ""
    echo "After installation, log out and back in, or run: newgrp docker"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker:"
    echo "  sudo systemctl start docker"
    exit 1
fi

# Check if already part of a swarm
if docker info | grep -q "Swarm: active"; then
    echo "⚠️  Already part of a Docker Swarm. Leaving current swarm..."
    docker swarm leave --force
fi

# Test connectivity to manager
echo "🔍 Testing connectivity to manager node..."
if ! ping -c 1 $MANAGER_IP &> /dev/null; then
    echo "⚠️  Warning: Cannot ping manager IP. This might be normal if ICMP is blocked."
fi

# Try to connect to Swarm port
echo "🔍 Testing Swarm port connectivity..."
if ! timeout 5 bash -c "</dev/tcp/$MANAGER_IP/2377" 2>/dev/null; then
    echo "❌ Cannot connect to Swarm port 2377 on $MANAGER_IP"
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "1. Check if port 2377 is open on the Azure VM:"
    echo "   sudo ufw allow 2377/tcp"
    echo ""
    echo "2. Check if the VM's network security group allows port 2377"
    echo "3. Try the direct Ray connection instead:"
    echo "   ./setup_laptop_worker.sh"
    exit 1
fi

echo "✅ Connectivity test passed!"

# Join the swarm
echo ""
echo "🔗 Joining Docker Swarm cluster..."
docker swarm join --token $JOIN_TOKEN $MANAGER_IP:2377

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully joined the Docker Swarm cluster!"
    echo ""
    echo "📊 Current node status:"
    echo "   docker node ls"
    echo ""
    echo "🔍 To check from the manager node, run:"
    echo "   docker node ls"
    echo ""
    echo "📈 To scale workers from the manager node:"
    echo "   docker service scale ray-cluster_ray-worker=3"
    echo ""
    echo "🎮 To test the cluster from the manager node:"
    echo "   docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest"
    echo ""
    echo "📊 Ray Dashboard: http://$MANAGER_IP:8265"
else
    echo "❌ Failed to join the Docker Swarm cluster"
    echo ""
    echo "🔧 Alternative: Use direct Ray connection"
    echo "   ./setup_laptop_worker.sh"
fi 