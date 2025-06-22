# Kubernetes Deployment for Distributed Ray Cluster

This directory contains Kubernetes manifests and scripts for deploying the distributed Ray cluster, designed to work both locally and across multiple machines.

## 🎯 **Multi-Machine Ready Design**

The Kubernetes setup is designed with multi-machine deployment in mind from the start:

- **Service Discovery**: Uses Kubernetes DNS for automatic service discovery
- **External Access**: NodePort services for cross-machine communication
- **Scalable Workers**: Deployment-based workers that can be scaled independently
- **Load Balancing**: Built-in Kubernetes load balancing
- **Health Monitoring**: Comprehensive health checks and monitoring

## 📁 **File Structure**

```
k8s/
├── namespace.yaml              # Ray cluster namespace
├── configmap.yaml              # Ray configuration
├── storage.yaml                # Persistent storage setup
├── ray-head-deployment.yaml    # Head node deployment
├── ray-head-service.yaml       # Head node services
├── ray-worker-deployment.yaml  # Worker node deployment
├── api-server-deployment.yaml  # API server deployment
├── api-server.py               # Flask API server
├── Dockerfile.api              # API server Dockerfile
├── deploy.sh                   # Deployment script
├── scale-workers.sh            # Worker scaling script
├── demo-client.py              # Demo client
└── README.md                   # This file
```

## 🚀 **Quick Start**

### **Prerequisites**

1. **Kubernetes Cluster**: Set up a Kubernetes cluster (minikube, kind, or cloud provider)
2. **kubectl**: Install and configure kubectl
3. **Docker Images**: Build the required Docker images

### **Build Docker Images**

```bash
# Build base image
docker build -f Dockerfile.base -t ray-cluster-base:latest .

# Build head node image
docker build -f Dockerfile.head -t ray-cluster-head:latest .

# Build worker node image
docker build -f Dockerfile.worker -t ray-cluster-worker:latest .

# Build API server image
docker build -f k8s/Dockerfile.api -t ray-cluster-api:latest .
```

### **Deploy the Cluster**

```bash
# Make scripts executable
chmod +x k8s/deploy.sh k8s/scale-workers.sh

# Deploy the entire cluster
./k8s/deploy.sh
```

### **Test the Deployment**

```bash
# Test the API
python k8s/demo-client.py

# Or use curl
curl -X POST http://localhost:30080/inference \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "What is machine learning?"}'
```

## 🌐 **Multi-Machine Deployment**

### **Single Machine (Current Setup)**

When running on a single machine, all components run in the same Kubernetes cluster:

```bash
# Deploy everything locally
./k8s/deploy.sh
```

### **Multi-Machine Setup**

When you're ready to move workers to other machines:

#### **Head Machine (Main Machine)**

1. **Deploy head node and API server**:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/storage.yaml
kubectl apply -f k8s/ray-head-deployment.yaml
kubectl apply -f k8s/ray-head-service.yaml
kubectl apply -f k8s/api-server-deployment.yaml
```

2. **Get external IP**:
```bash
# Get the external IP of your head machine
HEAD_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
echo "Head node IP: $HEAD_IP"
```

#### **Worker Machine (Other Machine)**

1. **Join the Kubernetes cluster** (if using multi-node cluster)
2. **Deploy worker with head node IP**:
```bash
# Set the head node IP
export HEAD_NODE_IP="YOUR_HEAD_MACHINE_IP"

# Deploy worker
kubectl apply -f k8s/ray-worker-deployment.yaml
```

3. **Update worker configuration** (if needed):
```bash
# Edit the worker deployment to use external head node IP
kubectl patch deployment ray-worker -n ray-cluster -p '{"spec":{"template":{"spec":{"containers":[{"name":"ray-worker","env":[{"name":"RAY_HEAD_ADDRESS","value":"'$HEAD_NODE_IP':30637"}]}]}}}}'
```

## 🔧 **Configuration Options**

### **Service Types**

- **NodePort**: For bare metal and local development
- **LoadBalancer**: For cloud environments
- **ClusterIP**: For internal communication only

### **Scaling Workers**

```bash
# Scale to 3 workers
./k8s/scale-workers.sh 3

# Or use kubectl directly
kubectl scale deployment ray-worker --replicas=3 -n ray-cluster
```

### **External Access**

The services expose the following ports:

- **Ray Head**: 30637 (Ray), 30826 (Dashboard), 31001 (Object Store)
- **API Server**: 30080 (HTTP API)

## 📊 **Monitoring and Debugging**

### **Check Cluster Status**

```bash
# View all pods
kubectl get pods -n ray-cluster

# View services
kubectl get svc -n ray-cluster

# View logs
kubectl logs -f deployment/ray-head -n ray-cluster
kubectl logs -f deployment/ray-worker -n ray-cluster
kubectl logs -f deployment/ray-api-server -n ray-cluster
```

### **Access Dashboard**

```bash
# Get dashboard URL
kubectl get svc ray-head-service -n ray-cluster -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
# Then visit: http://<IP>:30826
```

### **Health Checks**

```bash
# Check API health
curl http://localhost:30080/health

# Check cluster status
curl http://localhost:30080/cluster/status
```

## 🔄 **Migration from Docker Compose**

### **Key Differences**

| Feature | Docker Compose | Kubernetes |
|---------|---------------|------------|
| **Multi-machine** | Limited | Native support |
| **Scaling** | Manual | Automatic |
| **Service Discovery** | Internal network | DNS-based |
| **Load Balancing** | None | Built-in |
| **Health Monitoring** | Basic | Comprehensive |
| **Resource Management** | Limited | Advanced |

### **Migration Steps**

1. **Build Kubernetes images** from existing Dockerfiles
2. **Deploy using Kubernetes manifests**
3. **Update service discovery** to use Kubernetes DNS
4. **Configure external access** for multi-machine setup

## 🚀 **Future Enhancements**

### **Horizontal Pod Autoscaling**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ray-worker-hpa
  namespace: ray-cluster
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ray-worker
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### **Ingress Configuration**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ray-ingress
  namespace: ray-cluster
spec:
  rules:
  - host: ray-cluster.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ray-api-service
            port:
              number: 80
```

### **Persistent Volume Claims**

For production, consider using cloud storage:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ray-models-pvc
  namespace: ray-cluster
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: managed-nfs-storage  # Cloud-specific
  resources:
    requests:
      storage: 50Gi
```

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **Worker can't connect to head**:
   - Check head node IP and port
   - Verify network connectivity
   - Check firewall rules

2. **Pods not starting**:
   - Check resource limits
   - Verify image availability
   - Check logs for errors

3. **API not accessible**:
   - Verify service configuration
   - Check NodePort assignments
   - Test internal connectivity

### **Debug Commands**

```bash
# Check pod events
kubectl describe pod <pod-name> -n ray-cluster

# Check service endpoints
kubectl get endpoints -n ray-cluster

# Test internal connectivity
kubectl exec -it <pod-name> -n ray-cluster -- curl ray-head-service:6379

# Check DNS resolution
kubectl exec -it <pod-name> -n ray-cluster -- nslookup ray-head-service
```

## 📚 **Additional Resources**

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Ray on Kubernetes](https://docs.ray.io/en/latest/ray-core/scheduling/kubernetes/index.html)
- [Flask API Development](https://flask.palletsprojects.com/)

---

**Ready to deploy your distributed inference system across multiple machines! 🚀** 