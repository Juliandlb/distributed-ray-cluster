#!/bin/bash

# Ray Cluster Demo Verification Script
# This script checks if all components are working correctly

set -e

echo "🔍 Ray Cluster Demo Verification"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking Prerequisites..."
if command_exists docker; then
    print_status "OK" "Docker is installed"
else
    print_status "ERROR" "Docker is not installed"
    exit 1
fi

if docker info >/dev/null 2>&1; then
    print_status "OK" "Docker daemon is running"
else
    print_status "ERROR" "Docker daemon is not running"
    exit 1
fi

if docker info | grep -q "Swarm: active"; then
    print_status "OK" "Docker Swarm is initialized"
else
    print_status "WARN" "Docker Swarm is not initialized (will be done automatically)"
fi

echo ""

# Check Docker images
echo "🏗️  Checking Docker Images..."
images_ok=true
for image in "ray-cluster-head:latest" "ray-cluster-worker:latest" "ray-cluster-client:latest"; do
    if docker images | grep -q "$image"; then
        print_status "OK" "Image $image exists"
    else
        # In Docker Swarm, images might not show in local list but still be available
        if docker run --rm --network ray-cluster_ray-cluster "$image" echo "test" >/dev/null 2>&1; then
            print_status "OK" "Image $image is available (used by containers)"
        else
            print_status "ERROR" "Image $image is missing"
            images_ok=false
        fi
    fi
done

if [ "$images_ok" = false ]; then
    echo ""
    print_status "WARN" "Some images are missing. Run './rebuild.sh' to build them."
fi

echo ""

# Check Docker services
echo "🚀 Checking Docker Services..."
services_ok=true
if docker stack ls | grep -q "ray-cluster"; then
    print_status "OK" "Ray cluster stack exists"
    
    # Check each service
    while IFS= read -r line; do
        if [[ $line =~ ray-cluster_ray-(head|worker|client) ]]; then
            service_name=$(echo "$line" | awk '{print $2}')
            replicas=$(echo "$line" | awk '{print $4}')
            expected_replicas="1/1"
            
            if [ "$replicas" = "$expected_replicas" ]; then
                print_status "OK" "Service $service_name is running ($replicas)"
            else
                print_status "ERROR" "Service $service_name is not ready ($replicas)"
                services_ok=false
            fi
        fi
    done < <(docker stack services ray-cluster)
else
    print_status "ERROR" "Ray cluster stack does not exist"
    services_ok=false
fi

echo ""

# Check Docker containers
echo "📦 Checking Docker Containers..."
containers_ok=true
container_count=$(docker ps --filter "name=ray-cluster" --format "table {{.Names}}" | grep -c "ray-cluster" || true)
expected_containers=3

if [ "$container_count" -eq "$expected_containers" ]; then
    print_status "OK" "All $expected_containers containers are running"
    
    # Check container health
    while IFS= read -r line; do
        container_name=$(echo "$line" | awk '{print $1}')
        status=$(echo "$line" | awk '{print $2}')
        
        if [[ $status == *"healthy"* ]] || [[ $status == *"Up"* ]]; then
            print_status "OK" "Container $container_name is healthy"
        else
            print_status "WARN" "Container $container_name status: $status"
        fi
    done < <(docker ps --filter "name=ray-cluster" --format "table {{.Names}}\t{{.Status}}")
else
    print_status "ERROR" "Expected $expected_containers containers, found $container_count"
    containers_ok=false
fi

echo ""

# Check Ray cluster connectivity
echo "🔗 Checking Ray Cluster Connectivity..."
if [ "$services_ok" = true ] && [ "$containers_ok" = true ]; then
    # Wait a bit for services to be fully ready
    sleep 5
    
    # Test Ray connection
    if timeout 30 docker run --rm --network ray-cluster_ray-cluster ray-cluster-client:latest python -c "
import ray
try:
    ray.init(address='ray://ray-head:10001', namespace='default', log_to_driver=False)
    print('Connected to Ray cluster')
    
    # Try to find coordinator
    try:
        coordinator = ray.get_actor('prompt_coordinator', namespace='default')
        actor_count = ray.get(coordinator.get_actor_count.remote())
        print(f'Found coordinator with {actor_count} actors')
        exit(0)
    except Exception as e:
        print(f'Coordinator not ready yet: {e}')
        exit(1)
except Exception as e:
    print(f'Failed to connect: {e}')
    exit(1)
" >/dev/null 2>&1; then
        print_status "OK" "Ray cluster is accessible and coordinator is ready"
        ray_ok=true
    else
        print_status "WARN" "Ray cluster is accessible but coordinator may not be ready yet"
        ray_ok=false
    fi
else
    print_status "ERROR" "Cannot test Ray connectivity - services not ready"
    ray_ok=false
fi

echo ""

# Check resource usage
echo "💾 Checking Resource Usage..."
if command_exists docker; then
    echo "Memory usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep ray-cluster || true
    
    echo ""
    echo "Disk usage:"
    docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}" | head -5
fi

echo ""

# Summary
echo "📊 Verification Summary"
echo "======================"
if [ "$services_ok" = true ] && [ "$containers_ok" = true ]; then
    if [ "$ray_ok" = true ]; then
        print_status "OK" "🎉 Ray cluster demo is ready!"
        echo ""
        echo "🎮 To run the demo:"
        echo "   docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest"
        echo ""
        echo "📊 Monitor the cluster:"
        echo "   Ray Dashboard: http://localhost:8265"
        echo "   Service status: docker stack services ray-cluster"
        echo ""
        echo "🧹 To clean up:"
        echo "   ./cleanup.sh"
    else
        print_status "WARN" "⚠️  Ray cluster is running but coordinator may need more time"
        echo ""
        echo "⏳ The cluster is starting up. Wait 1-2 minutes and try again."
        echo "🎮 To test the demo:"
        echo "   docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest"
        echo ""
        echo "📊 Monitor startup:"
        echo "   docker service logs ray-cluster_ray-head -f"
    fi
else
    print_status "ERROR" "❌ Ray cluster demo is not ready"
    echo ""
    echo "🔧 To fix issues:"
    echo "   1. Run './rebuild.sh' to rebuild everything"
    echo "   2. Check logs: docker service logs ray-cluster_ray-head"
    echo "   3. Check memory: docker stats --no-stream"
    echo "   4. Wait for initialization (can take 1-2 minutes)"
fi

echo "" 