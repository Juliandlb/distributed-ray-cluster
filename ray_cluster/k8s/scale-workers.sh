#!/bin/bash

# Scale worker nodes in the Ray cluster

REPLICAS=${1:-1}

echo "🔧 Scaling Ray worker nodes to $REPLICAS replicas..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Scale the worker deployment
kubectl scale deployment ray-worker --replicas=$REPLICAS -n ray-cluster

echo "✅ Worker nodes scaled to $REPLICAS replicas"

# Wait for pods to be ready
echo "⏳ Waiting for worker pods to be ready..."
kubectl wait --for=condition=ready pod -l app=ray-worker -n ray-cluster --timeout=300s

# Show current status
echo ""
echo "📊 Current cluster status:"
kubectl get pods -n ray-cluster

echo ""
echo "🔍 Check worker logs:"
echo "   kubectl logs -f deployment/ray-worker -n ray-cluster"

echo ""
echo "📈 Monitor scaling:"
echo "   kubectl get deployment ray-worker -n ray-cluster" 