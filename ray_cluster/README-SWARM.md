# Docker Swarm Migration for Distributed Ray Cluster

This document describes the migration from Docker Compose to Docker Swarm for multi-machine distributed Ray cluster deployment.

## 🎯 **Why Docker Swarm?**

### **Docker Compose Limitations:**
- ❌ **Single Machine Only**: Cannot orchestrate containers across multiple machines
- ❌ **No Built-in Scaling**: Manual container management required
- ❌ **No High Availability**: No automatic failover or recovery
- ❌ **Limited Networking**: No overlay networks for multi-machine communication

### **Docker Swarm Benefits:**
- ✅ **Multi-Machine Support**: Orchestrate containers across multiple nodes
- ✅ **Automatic Scaling**: Scale services up/down with simple commands
- ✅ **High Availability**: Automatic failover and recovery
- ✅ **Overlay Networking**: Seamless communication between nodes
- ✅ **Load Balancing**: Built-in load balancing across nodes
- ✅ **Service Discovery**: Automatic service discovery and routing
- ✅ **Rolling Updates**: Zero-downtime deployments

## 🏗️ **Architecture Overview**

### **Single Machine (Docker Compose):**
```
Machine 1:
├── Head Node (Coordinator)
└── Worker Node (Inference)
```

### **Multi-Machine (Docker Swarm):**
```
Manager Node (Machine 1):
├── Head Node (Coordinator)
└── Worker Node (Inference)

Worker Node (Machine 2):
└── Worker Node (Inference)

Worker Node (Machine 3):
└── Worker Node (Inference)
```

## 🚀 **Quick Start**

### **Step 1: Build Images**
```bash
# Make scripts executable
chmod +x build-swarm.sh deploy-swarm.sh join-worker.sh

# Build all required images
./build-swarm.sh
```

### **Step 2: Deploy on Manager Node**
```bash
# Deploy the complete cluster
./deploy-swarm.sh deploy
```

### **Step 3: Add Worker Nodes (Optional)**
```bash
# On other machines, join as worker nodes
./join-worker.sh <manager_ip>
```

## 📋 **Detailed Setup Instructions**

### **Prerequisites**

1. **Docker**: Latest version installed on all machines
2. **SSH Access**: Key-based SSH between manager and worker nodes
3. **Network**: All machines can communicate on ports 2377, 7946, 4789
4. **Resources**: Minimum 4GB RAM, 2 CPU cores per machine

### **Manager Node Setup**

1. **Build Images:**
   ```bash
   cd /path/to/ray_cluster
   ./build-swarm.sh
   ```

2. **Deploy Cluster:**
   ```bash
   ./deploy-swarm.sh deploy
   ```

3. **Verify Deployment:**
   ```bash
   ./deploy-swarm.sh status
   ```

### **Worker Node Setup**

1. **Copy Scripts:**
   ```bash
   # Copy the join-worker.sh script to worker machine
   scp join-worker.sh user@worker-machine:/path/to/ray_cluster/
   ```

2. **Join Swarm:**
   ```bash
   # On worker machine
   cd /path/to/ray_cluster
   chmod +x join-worker.sh
   ./join-worker.sh <manager_ip>
   ```

3. **Verify Connection:**
   ```bash
   # On manager node
   docker node ls
   ```

## 🔧 **Configuration Files**

### **docker-swarm.yml**
Main Docker Swarm stack configuration with:
- **ray-head**: Coordinator service (1 replica, manager node only)
- **ray-worker**: Inference service (scalable, worker nodes)
- **Overlay Network**: Multi-machine communication
- **Resource Limits**: Memory and CPU constraints
- **Health Checks**: Automatic health monitoring
- **Rolling Updates**: Zero-downtime deployments

### **Key Features:**
- **Placement Constraints**: Head node on manager, workers on worker nodes
- **Resource Management**: Memory and CPU limits per service
- **Service Discovery**: Automatic service discovery via overlay network
- **Load Balancing**: Built-in load balancing across nodes
- **Health Monitoring**: Automatic health checks and recovery

## 🛠️ **Management Commands**

### **Cluster Management**
```bash
# Deploy cluster
./deploy-swarm.sh deploy

# Check status
./deploy-swarm.sh status

# View logs
./deploy-swarm.sh logs

# Scale workers
./deploy-swarm.sh scale 5

# Remove cluster
./deploy-swarm.sh remove
```

### **Docker Swarm Commands**
```bash
# List nodes
docker node ls

# List services
docker service ls

# Scale service
docker service scale ray-cluster_ray-worker=3

# View service logs
docker service logs ray-cluster_ray-worker

# Update service
docker service update ray-cluster_ray-worker

# Remove service
docker service rm ray-cluster_ray-worker
```

### **Node Management**
```bash
# List nodes
docker node ls

# Inspect node
docker node inspect <node_id>

# Update node labels
docker node update --label-add zone=us-west <node_id>

# Drain node (maintenance)
docker node update --availability drain <node_id>

# Activate node
docker node update --availability active <node_id>
```

## 📊 **Scaling and Performance**

### **Horizontal Scaling**
```bash
# Scale to 3 workers
docker service scale ray-cluster_ray-worker=3

# Scale to 5 workers
docker service scale ray-cluster_ray-worker=5

# Scale to 10 workers
docker service scale ray-cluster_ray-worker=10
```

### **Resource Allocation**
- **Head Node**: 1 CPU, 2GB RAM (coordinator only)
- **Worker Node**: 2 CPU, 3GB RAM (inference engines)
- **Total per Worker**: ~2.5GB memory usage

### **Performance Benefits**
- **Load Distribution**: Tasks automatically distributed across nodes
- **Fault Tolerance**: If one node fails, others continue
- **Resource Utilization**: Better CPU and memory usage
- **Scalability**: Add nodes without restarting cluster

## 🔍 **Monitoring and Debugging**

### **Cluster Monitoring**
```bash
# Ray Dashboard
http://localhost:8265

# Docker Swarm Dashboard
docker service ls
docker stack ps ray-cluster

# Node Status
docker node ls
docker node inspect <node_id>
```

### **Service Logs**
```bash
# Head node logs
docker service logs ray-cluster_ray-head

# Worker node logs
docker service logs ray-cluster_ray-worker

# Follow logs in real-time
docker service logs -f ray-cluster_ray-worker
```

### **Health Checks**
```bash
# Check service health
docker service ls --format "table {{.Name}}\t{{.Replicas}}\t{{.Ports}}"

# Check node health
docker node ls --format "table {{.Hostname}}\t{{.Status}}\t{{.Availability}}"
```

## 🌐 **Network Configuration**

### **Port Requirements**
- **2377**: Docker Swarm cluster management
- **7946**: Docker Swarm node communication
- **4789**: Docker Swarm overlay network
- **6379**: Ray cluster communication
- **8265**: Ray dashboard

### **Firewall Configuration**
```bash
# On all nodes, open required ports
sudo ufw allow 2377/tcp
sudo ufw allow 7946/tcp
sudo ufw allow 7946/udp
sudo ufw allow 4789/udp
sudo ufw allow 6379/tcp
sudo ufw allow 8265/tcp
```

## 🔄 **Migration from Docker Compose**

### **Step 1: Stop Docker Compose**
```bash
# Stop existing compose services
docker-compose -f docker-compose.laptop.yml down
```

### **Step 2: Build Swarm Images**
```bash
# Build new swarm images
./build-swarm.sh
```

### **Step 3: Deploy Swarm Stack**
```bash
# Deploy swarm stack
./deploy-swarm.sh deploy
```

### **Step 4: Verify Migration**
```bash
# Check services are running
./deploy-swarm.sh status

# Test functionality
docker exec -it $(docker ps -q -f name=ray-cluster) python real_interactive_prompts.py
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Node Cannot Join Swarm**
   ```bash
   # Check network connectivity
   ping <manager_ip>
   
   # Check Docker Swarm status
   docker info | grep Swarm
   
   # Check join token
   docker swarm join-token worker
   ```

2. **Services Not Starting**
   ```bash
   # Check service logs
   docker service logs <service_name>
   
   # Check node resources
   docker node inspect <node_id>
   
   # Check placement constraints
   docker service inspect <service_name>
   ```

3. **Network Issues**
   ```bash
   # Check overlay network
   docker network ls
   docker network inspect ray-cluster_ray-cluster
   
   # Check service connectivity
   docker service exec <service_name> ping <other_service>
   ```

### **Debug Commands**
```bash
# Check swarm status
docker info | grep Swarm

# Check node status
docker node ls

# Check service status
docker service ls

# Check network status
docker network ls

# Check volume status
docker volume ls
```

## 📈 **Advanced Configuration**

### **Custom Resource Limits**
Edit `docker-swarm.yml` to adjust resource limits:
```yaml
deploy:
  resources:
    limits:
      memory: 4G  # Increase memory limit
      cpus: '4.0'  # Increase CPU limit
    reservations:
      memory: 2G
      cpus: '2.0'
```

### **Placement Constraints**
Add custom placement constraints:
```yaml
deploy:
  placement:
    constraints:
      - node.role == worker
      - node.labels.zone == us-west
    preferences:
      - spread: node.labels.datacenter
```

### **Update Strategies**
Configure rolling updates:
```yaml
deploy:
  update_config:
    parallelism: 2
    delay: 10s
    order: start-first
    failure_action: rollback
  rollback_config:
    parallelism: 1
    delay: 5s
    order: stop-first
```

## 🎉 **Benefits Achieved**

### **Multi-Machine Support**
- ✅ Distribute Ray workers across multiple machines
- ✅ Automatic load balancing across nodes
- ✅ Fault tolerance and high availability

### **Scalability**
- ✅ Easy horizontal scaling with `docker service scale`
- ✅ Automatic resource distribution
- ✅ Dynamic worker addition/removal

### **Management**
- ✅ Centralized cluster management
- ✅ Built-in monitoring and health checks
- ✅ Rolling updates and rollbacks

### **Networking**
- ✅ Overlay networks for seamless communication
- ✅ Automatic service discovery
- ✅ Load balancing across nodes

## 🔮 **Future Enhancements**

### **Planned Features**
- **GPU Support**: Multi-GPU node support
- **Persistent Storage**: Distributed storage solutions
- **Monitoring**: Prometheus/Grafana integration
- **Security**: TLS encryption and authentication
- **Backup**: Automated backup and recovery

### **Integration Options**
- **Kubernetes**: Migration path to Kubernetes
- **Cloud Providers**: AWS, GCP, Azure integration
- **CI/CD**: Automated deployment pipelines
- **Monitoring**: Advanced monitoring and alerting

---

**🎯 Ready to scale your Ray cluster across multiple machines with Docker Swarm!** 