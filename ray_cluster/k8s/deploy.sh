#!/bin/bash

# Deploy the entire Ray cluster to Kubernetes
# Works for both single-machine and multi-machine setups

set -e

echo "🚀 Deploying Ray Cluster to Kubernetes..."
echo "📋 This setup is designed for multi-machine deployment"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Not connected to a Kubernetes cluster. Please set up your cluster first."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster: $(kubectl config current-context)"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f "$SCRIPT_DIR/namespace.yaml"

# Create storage
echo "💾 Setting up storage..."
kubectl apply -f "$SCRIPT_DIR/storage.yaml"

# Create config
echo "⚙️  Creating configuration..."
kubectl apply -f "$SCRIPT_DIR/configmap.yaml"

# Deploy head node
echo "🎯 Deploying head node..."
kubectl apply -f "$SCRIPT_DIR/ray-head-deployment.yaml"
kubectl apply -f "$SCRIPT_DIR/ray-head-service.yaml"

# Wait for head node to be ready
echo "⏳ Waiting for head node to be ready..."
kubectl wait --for=condition=ready pod -l app=ray-head -n ray-cluster --timeout=300s

# Deploy API server
echo "🌐 Deploying API server..."
kubectl apply -f "$SCRIPT_DIR/api-server-deployment.yaml"

# Wait for API server to be ready
echo "⏳ Waiting for API server to be ready..."
kubectl wait --for=condition=ready pod -l app=ray-api-server -n ray-cluster --timeout=120s

# Deploy worker nodes
echo "🔧 Deploying worker nodes..."
kubectl apply -f "$SCRIPT_DIR/ray-worker-deployment.yaml"

# Wait for worker to be ready
echo "⏳ Waiting for worker to be ready..."
kubectl wait --for=condition=ready pod -l app=ray-worker -n ray-cluster --timeout=300s

echo ""
echo "✅ Ray cluster deployed successfully!"
echo ""

# Get service information
echo "📊 Service Information:"
echo "========================"

# Get head node service info
HEAD_SERVICE=$(kubectl get svc ray-head-service -n ray-cluster -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "N/A")
if [ "$HEAD_SERVICE" = "N/A" ]; then
    HEAD_SERVICE=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}' 2>/dev/null || kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
fi

# Get API service info
API_SERVICE=$(kubectl get svc ray-api-service -n ray-cluster -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "N/A")
if [ "$API_SERVICE" = "N/A" ]; then
    API_SERVICE=$HEAD_SERVICE
fi

echo "🎯 Ray Head Node:"
echo "   Dashboard: http://$HEAD_SERVICE:30826"
echo "   Ray Port: $HEAD_SERVICE:30637"
echo "   Object Store: $HEAD_SERVICE:31001"

echo ""
echo "🌐 API Server:"
echo "   API: http://$API_SERVICE:30080"
echo "   Health Check: http://$API_SERVICE:30080/health"

echo ""
echo "🔧 Cluster Status:"
echo "   kubectl get pods -n ray-cluster"
echo "   kubectl logs -f deployment/ray-head -n ray-cluster"
echo "   kubectl logs -f deployment/ray-worker -n ray-cluster"

echo ""
echo "🚀 Test the API:"
echo "   curl -X POST http://$API_SERVICE:30080/inference \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"prompt\": \"What is machine learning?\"}'"

echo ""
echo "📋 For multi-machine deployment:"
echo "   1. Deploy head node on the main machine"
echo "   2. Deploy worker nodes on other machines"
echo "   3. Use the external service addresses for communication" 