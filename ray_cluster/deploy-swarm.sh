#!/bin/bash

# Docker Swarm Deployment Script for Ray Cluster
# This script handles the complete deployment process

set -e

STACK_NAME="ray-cluster"
COMPOSE_FILE="docker-swarm.yml"

echo "🚀 [DEPLOYING] Docker Swarm Ray Cluster"
echo "======================================="

# Function to check if Docker Swarm is initialized
check_swarm() {
    if ! docker info | grep -q "Swarm: active"; then
        echo "⚠️  [WARNING] Docker Swarm not initialized"
        echo "🔧 [INITIALIZING] Docker Swarm..."
        docker swarm init
        echo "✅ [SUCCESS] Docker Swarm initialized"
    else
        echo "✅ [CHECK] Docker Swarm is active"
    fi
}

# Function to deploy the stack
deploy_stack() {
    echo "📦 [DEPLOYING] Ray cluster stack..."
    
    # Check if stack already exists
    if docker stack ls | grep -q "$STACK_NAME"; then
        echo "🔄 [UPDATING] Existing stack..."
        docker stack deploy -c "$COMPOSE_FILE" "$STACK_NAME"
    else
        echo "🆕 [CREATING] New stack..."
        docker stack deploy -c "$COMPOSE_FILE" "$STACK_NAME"
    fi
    
    echo "✅ [SUCCESS] Stack deployed successfully"
}

# Function to wait for services to be ready
wait_for_services() {
    echo "⏳ [WAITING] For services to be ready..."
    
    # Wait for head node
    echo "🎯 [WAITING] Head node to be ready..."
    while ! docker service ls | grep "$STACK_NAME" | grep "ray-head" | grep -q "1/1"; do
        sleep 5
        echo "   Still waiting for head node..."
    done
    echo "✅ [SUCCESS] Head node is ready"
    
    # Wait for worker nodes
    echo "🤖 [WAITING] Worker nodes to be ready..."
    while ! docker service ls | grep "$STACK_NAME" | grep "ray-worker" | grep -q "2/2"; do
        sleep 5
        echo "   Still waiting for worker nodes..."
    done
    echo "✅ [SUCCESS] Worker nodes are ready"
}

# Function to show cluster status
show_status() {
    echo ""
    echo "📊 [CLUSTER STATUS]"
    echo "==================="
    
    echo "🏗️  [STACK] $STACK_NAME"
    docker stack ls | grep "$STACK_NAME"
    
    echo ""
    echo "🔧 [SERVICES]"
    docker stack services "$STACK_NAME"
    
    echo ""
    echo "🖥️  [NODES]"
    docker node ls
    
    echo ""
    echo "📦 [TASKS]"
    docker stack ps "$STACK_NAME"
}

# Function to show logs
show_logs() {
    echo ""
    echo "📋 [LOGS] Recent logs from services:"
    echo "===================================="
    
    echo "🎯 [HEAD NODE LOGS]"
    docker service logs "$STACK_NAME"_ray-head --tail 10 2>/dev/null || echo "   No logs available yet"
    
    echo ""
    echo "🤖 [WORKER NODE LOGS]"
    docker service logs "$STACK_NAME"_ray-worker --tail 10 2>/dev/null || echo "   No logs available yet"
}

# Function to scale workers
scale_workers() {
    local count=${1:-3}
    echo "📈 [SCALING] Worker nodes to $count replicas..."
    docker service scale "$STACK_NAME"_ray-worker=$count
    echo "✅ [SUCCESS] Worker nodes scaled to $count"
}

# Function to remove stack
remove_stack() {
    echo "🗑️  [REMOVING] Stack $STACK_NAME..."
    docker stack rm "$STACK_NAME"
    echo "✅ [SUCCESS] Stack removed"
}

# Main execution
case "${1:-deploy}" in
    "deploy")
        check_swarm
        deploy_stack
        wait_for_services
        show_status
        show_logs
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "scale")
        scale_workers "$2"
        ;;
    "remove")
        remove_stack
        ;;
    "init")
        check_swarm
        ;;
    *)
        echo "Usage: $0 [deploy|status|logs|scale <count>|remove|init]"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy the Ray cluster (default)"
        echo "  status  - Show cluster status"
        echo "  logs    - Show service logs"
        echo "  scale   - Scale worker nodes (e.g., scale 5)"
        echo "  remove  - Remove the stack"
        echo "  init    - Initialize Docker Swarm only"
        exit 1
        ;;
esac

echo ""
echo "🎉 [COMPLETE] Docker Swarm Ray Cluster deployment finished!"
echo ""
echo "🔗 [ACCESS]"
echo "   Ray Dashboard: http://localhost:8265"
echo "   Ray Port: localhost:6379"
echo ""
echo "🛠️  [MANAGEMENT]"
echo "   Check status: ./deploy-swarm.sh status"
echo "   View logs: ./deploy-swarm.sh logs"
echo "   Scale workers: ./deploy-swarm.sh scale 5"
echo "   Remove cluster: ./deploy-swarm.sh remove" 