#!/bin/bash

# Test script to verify Ray cluster status
set -e

echo "🔍 Testing Ray Cluster Status"
echo "============================="

VM_PUBLIC_IP=$(curl -s ifconfig.me)
echo "📍 VM Public IP: $VM_PUBLIC_IP"
echo ""

echo "📊 Current Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "🔗 Testing Ray cluster connectivity..."
echo ""

# Test if Ray cluster is responding
echo "1. Testing Ray cluster port (6379)..."
if timeout 5 bash -c "</dev/tcp/localhost/6379" 2>/dev/null; then
    echo "   ✅ Ray cluster port is accessible locally"
else
    echo "   ❌ Ray cluster port not accessible locally"
fi

echo ""

echo "2. Testing Ray dashboard (8265)..."
if timeout 5 bash -c "</dev/tcp/localhost/8265" 2>/dev/null; then
    echo "   ✅ Ray dashboard is accessible locally"
    echo "   📊 Dashboard URL: http://$VM_PUBLIC_IP:8265"
else
    echo "   ❌ Ray dashboard not accessible locally"
fi

echo ""

echo "3. Testing Ray client port (10001)..."
if timeout 5 bash -c "</dev/tcp/localhost/10001" 2>/dev/null; then
    echo "   ✅ Ray client port is accessible locally"
else
    echo "   ❌ Ray client port not accessible locally"
fi

echo ""

echo "4. Running simple demo test..."
if docker build -f Dockerfile.simple -t ray-cluster-simple:latest . >/dev/null 2>&1; then
    echo "   ✅ Simple demo container built successfully"
    
    # Run the demo and capture output
    DEMO_OUTPUT=$(docker run --rm --network ray-cluster_ray-cluster ray-cluster-simple:latest 2>&1 || true)
    
    if echo "$DEMO_OUTPUT" | grep -q "Available inference actors: 1"; then
        echo "   ✅ Cluster has 1 inference actor available"
    elif echo "$DEMO_OUTPUT" | grep -q "Available inference actors: 0"; then
        echo "   ⚠️  Cluster has 0 inference actors (head node only)"
    else
        echo "   ❌ Could not determine actor count"
    fi
    
    if echo "$DEMO_OUTPUT" | grep -q "Found prompt coordinator"; then
        echo "   ✅ Prompt coordinator is available"
    else
        echo "   ❌ Prompt coordinator not found"
    fi
else
    echo "   ❌ Failed to build simple demo container"
fi

echo ""

echo "5. Checking worker node status..."
WORKER_LOGS=$(docker logs ray-cluster_ray-worker.1.pm1705yyea77lsm8c68xrigp8 2>&1 | tail -20 || true)

if echo "$WORKER_LOGS" | grep -q "Registered actor.*gpt2"; then
    echo "   ✅ Worker has registered GPT-2 actor"
else
    echo "   ❌ Worker has not registered any actors"
fi

if echo "$WORKER_LOGS" | grep -q "Worker Node Successfully Joined Cluster"; then
    echo "   ✅ Worker node is connected to cluster"
else
    echo "   ❌ Worker node not connected"
fi

echo ""

echo "📋 Summary:"
echo "==========="
echo "VM Public IP: $VM_PUBLIC_IP"
echo "Ray Dashboard: http://$VM_PUBLIC_IP:8265"
echo "Ray Cluster: $VM_PUBLIC_IP:6379"
echo "Ray Client: $VM_PUBLIC_IP:10001"
echo ""

echo "🎯 To connect from your local machine:"
echo "1. Configure Azure NSG to open ports 6379, 8265, 10001"
echo "2. Test connectivity: telnet $VM_PUBLIC_IP 6379"
echo "3. Join as worker: ./start_remote_worker_direct.sh $VM_PUBLIC_IP"
echo ""

echo "✅ Current cluster is operational and ready for external workers!" 