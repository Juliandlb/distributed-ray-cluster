# 🖥️ VM + Remote Worker Multi-Machine Setup

This guide is specifically for your setup:
- **VM (Head Node)**: `10.11.0.4` - Running the Ray cluster coordinator
- **Remote Worker Node**: Your personal machine - Running the remote worker

## 🖥️ **Step 1: VM Head Node Setup**

### **1.1 Start the Cluster on VM**
```bash
# On your VM (current machine)
cd /home/julian/distributed-ray-cluster/ray_cluster
./start_cluster.sh
```

**Expected Output:**
```
🚀 Starting Ray Cluster (Head Node)
==================================
📍 Head Node IP: 10.11.0.4
🔧 Initializing Docker Swarm...
🔨 Building and deploying Ray cluster...
⏳ Waiting for services to be ready...

🎯 CLUSTER READY!
==================
📍 Head Node IP: 10.11.0.4
🔌 Ray Port: 6379
📊 Dashboard: http://10.11.0.4:8265

🔗 To connect a remote worker, run:
   ./start_standalone_worker.sh 10.11.0.4

✅ Cluster is running and ready for remote workers!
```

### **1.2 Verify VM Head Node**
```bash
# Check if services are running
docker stack services ray-cluster

# Check if ports are exposed
netstat -tlnp | grep -E ':(6379|8265|10001|12345|12346)'

# Test Ray dashboard
curl http://localhost:8265
```

## 💻 **Step 2: Remote Worker Node Setup**

### **2.1 Prepare Your Remote Worker Node**

First, ensure Docker is installed on your remote worker node:
```bash
# Install Docker (if not already installed)
# For Arch Linux:
sudo pacman -S docker

# For Ubuntu/Debian:
sudo apt update && sudo apt install docker.io

# For CentOS/RHEL:
sudo yum install docker

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (if needed)
sudo usermod -aG docker $USER
# Log out and back in, or run: newgrp docker
```

### **2.2 Clone the Repository**
```bash
# On your remote worker node
git clone https://github.com/Juliandlb/distributed-ray-cluster.git
cd distributed-ray-cluster/ray_cluster
```

### **2.3 Test Network Connectivity**
```bash
# Test connectivity to VM
ping 10.11.0.4

# Test Ray port connectivity
telnet 10.11.0.4 6379

# Test dashboard connectivity
curl http://10.11.0.4:8265
```

### **2.4 Start Remote Worker**
```bash
# Make script executable
chmod +x start_standalone_worker.sh

# Start the remote worker
./start_standalone_worker.sh 10.11.0.4
```

**Expected Output:**
```
🤖 Starting Standalone Ray Worker
================================
📍 Worker IP: [your-laptop-ip]
🔗 Connecting to Head: 10.11.0.4:6379
🔨 Building worker image...
🚀 Starting standalone worker container...

✅ Standalone worker started!
============================
📍 Worker IP: [your-laptop-ip]
🔗 Connected to: 10.11.0.4:6379
```

## 🎮 **Step 3: Test the Multi-Machine Cluster**

### **3.1 From VM (Head Node)**
```bash
# Test the cluster from the VM
docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest
```

### **3.2 From Remote Worker Node**
```bash
# You can also test from your remote worker (if you have the client image)
docker run --rm -it ray-cluster-client:latest
```

## 📊 **Step 4: Monitor the Cluster**

### **4.1 Ray Dashboard**
- **URL**: http://10.11.0.4:8265
- **Check**: Should show both VM head node and remote worker
- **Nodes**: Should see 2 nodes (VM + remote worker)

### **4.2 Check Worker Status**
```bash
# On remote worker node
docker ps | grep ray-standalone-worker
docker logs ray-standalone-worker

# On VM
docker stack services ray-cluster
docker service logs ray-cluster_ray-head
```

## 🔧 **Step 5: Troubleshooting**

### **5.1 Network Issues**
```bash
# From remote worker node, test connectivity
ping 10.11.0.4
telnet 10.11.0.4 6379
curl http://10.11.0.4:8265

# If telnet fails, check if ports are open on VM
# On VM:
sudo netstat -tlnp | grep 6379
```

### **5.2 Firewall Issues**
If you can't connect from remote worker to VM:

**On VM (if using UFW):**
```bash
sudo ufw allow 6379
sudo ufw allow 8265
sudo ufw allow 12345:12346
```

**On VM (if using iptables):**
```bash
sudo iptables -A INPUT -p tcp --dport 6379 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8265 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 12345:12346 -j ACCEPT
```

### **5.3 Docker Issues on Remote Worker**
```bash
# If Docker doesn't work on remote worker
sudo systemctl status docker
sudo journalctl -u docker

# Reinstall Docker if needed
# For Arch Linux:
sudo pacman -R docker
sudo pacman -S docker

# For Ubuntu/Debian:
sudo apt remove docker.io
sudo apt install docker.io

# For CentOS/RHEL:
sudo yum remove docker
sudo yum install docker

sudo systemctl start docker
```

## 🧹 **Step 6: Cleanup**

### **6.1 Stop Remote Worker**
```bash
# On your remote worker node
docker stop ray-standalone-worker
docker rm ray-standalone-worker
```

### **6.2 Stop Head Cluster (VM)**
```bash
# On your VM
./cleanup.sh
```

## 🎯 **Expected Results**

When everything works correctly:

1. **VM Dashboard**: http://10.11.0.4:8265 shows 2 nodes
2. **Interactive Test**: Prompts are processed on your remote worker node
3. **Response Info**: Shows your remote worker's hostname and IP in responses
4. **Real Multi-Machine**: Processing happens across different physical machines

## 🚀 **Quick Test Commands**

```bash
# On VM - Start cluster
./start_cluster.sh

# On remote worker node - Join as worker
./start_standalone_worker.sh 10.11.0.4

# On VM - Test the cluster
docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest
```

Your VM + remote worker setup is ready! 🎉 