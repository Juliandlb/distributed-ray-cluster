# 🔍 Detailed Multi-Machine Testing Guide

This guide explains exactly how to test the multi-machine Ray cluster setup, including all ports, configuration, and troubleshooting.

## 📋 **Prerequisites & Ports**

### **Required Ports (All configured in code)**

| **Port** | **Service** | **Purpose** | **Configured In** |
|----------|-------------|-------------|-------------------|
| **6379** | Ray Core | Main Ray communication | `docker-swarm.yml` + `start_head.sh` |
| **8265** | Ray Dashboard | Web UI for monitoring | `docker-swarm.yml` + `start_head.sh` |
| **10001** | Ray Client | Client connections | `docker-swarm.yml` + `start_head.sh` |
| **12345** | Object Manager | Data transfer | `docker-swarm.yml` |
| **12346** | Node Manager | Node management | `docker-swarm.yml` |
| **10003** | Object Manager Comm | Additional data comm | `docker-swarm.yml` |

### **Network Requirements**

- **Head Node**: Must expose all ports to external network
- **Remote Workers**: Must be able to reach head node on port 6379
- **Firewall**: Open ports 6379, 8265, 12345-12346 on head node

## 🖥️ **Step 1: Head Node Setup (Machine 1)**

### **1.1 Check Current Setup**
```bash
# Check if Docker is running
docker --version

# Check if ports are available
netstat -tlnp | grep -E ':(6379|8265|10001|12345|12346)'

# Check current IP
hostname -I
```

### **1.2 Start the Cluster**
```bash
cd /path/to/ray_cluster
./start_cluster.sh
```

**Expected Output:**
```
🚀 Starting Ray Cluster (Head Node)
==================================
📍 Head Node IP: 192.168.1.100
🔧 Initializing Docker Swarm...
🔨 Building and deploying Ray cluster...
⏳ Waiting for services to be ready...

🎯 CLUSTER READY!
==================
📍 Head Node IP: 192.168.1.100
🔌 Ray Port: 6379
📊 Dashboard: http://192.168.1.100:8265

✅ Cluster is running and ready for remote workers!
```

### **1.3 Verify Head Node**
```bash
# Check services are running
docker stack services ray-cluster

# Check containers
docker ps | grep ray-cluster

# Check Ray dashboard
curl http://localhost:8265

# Check Ray port
telnet localhost 6379
```

## 🤖 **Step 2: Remote Worker Setup (Machine 2)**

### **2.1 Network Connectivity Test**
```bash
# Test connectivity to head node
ping 192.168.1.100

# Test Ray port connectivity
telnet 192.168.1.100 6379

# Test dashboard connectivity
curl http://192.168.1.100:8265
```

### **2.2 Start Remote Worker**
```bash
cd /path/to/ray_cluster
./start_standalone_worker.sh 192.168.1.100
```

**Expected Output:**
```
🤖 Starting Standalone Ray Worker
================================
📍 Worker IP: 192.168.1.101
🔗 Connecting to Head: 192.168.1.100:6379
🔨 Building worker image...
🚀 Starting standalone worker container...

✅ Standalone worker started!
============================
📍 Worker IP: 192.168.1.101
🔗 Connected to: 192.168.1.100:6379
```

### **2.3 Verify Remote Worker**
```bash
# Check worker container
docker ps | grep ray-standalone-worker

# Check worker logs
docker logs ray-standalone-worker

# Check if worker joined cluster (from head node)
curl http://192.168.1.100:8265
```

## 🎮 **Step 3: Test the Multi-Machine Cluster**

### **3.1 Interactive Testing**
```bash
# From head node machine
docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest
```

**Expected Interaction:**
```
🎮 [REAL INTERACTIVE PROMPTS] Distributed Ray Cluster Client
============================================================
🔗 Connecting to Ray cluster...
✅ Connected to Ray cluster
🎯 [COORDINATOR] Looking for prompt coordinator...
✅ Found prompt coordinator
🤖 Available inference actors: 1

🎮 [INTERACTIVE MODE] Type your prompts below
=============================================

🤖 [PROMPT] hello world
📤 [SENDING] Sending to coordinator...
📥 [RESPONSE] Received in 2.34s

💬 [RESPONSES]
   ✅ Actor 0 (gpt2)
      Worker Node #1: worker-machine (192.168.1.101)
      Processing time: 2.34s
      Response: Hello world! How can I help you today?

🎯 [ANSWERED BY] Worker Node #1
   Hostname: worker-machine (192.168.1.101)
   Model: gpt2
   Processing time: 2.34s
```

### **3.2 Dashboard Verification**
- **URL**: http://192.168.1.100:8265
- **Check**: Should show both head node and remote worker
- **Nodes**: Should see 2 nodes (head + remote worker)
- **Actors**: Should see inference actors running on remote worker

## 🔧 **Step 4: Troubleshooting**

### **4.1 Port Issues**
```bash
# Check if ports are open on head node
sudo netstat -tlnp | grep -E ':(6379|8265|10001|12345|12346)'

# Check firewall (Ubuntu/Debian)
sudo ufw status
sudo ufw allow 6379
sudo ufw allow 8265
sudo ufw allow 12345:12346

# Check firewall (CentOS/RHEL)
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-port=6379/tcp
sudo firewall-cmd --permanent --add-port=8265/tcp
sudo firewall-cmd --permanent --add-port=12345-12346/tcp
sudo firewall-cmd --reload
```

### **4.2 Network Connectivity**
```bash
# From remote worker machine
ping 192.168.1.100
telnet 192.168.1.100 6379
curl http://192.168.1.100:8265

# Check Docker network
docker network ls
docker network inspect ray-cluster_ray-cluster
```

### **4.3 Service Issues**
```bash
# Check head node services
docker stack services ray-cluster
docker service logs ray-cluster_ray-head

# Check remote worker
docker logs ray-standalone-worker
docker exec ray-standalone-worker ps aux
```

### **4.4 Ray Connection Issues**
```bash
# Check Ray processes on head node
docker exec $(docker ps -q --filter "name=ray-cluster_ray-head") ps aux | grep ray

# Check Ray processes on remote worker
docker exec ray-standalone-worker ps aux | grep ray

# Check Ray logs
docker exec $(docker ps -q --filter "name=ray-cluster_ray-head") tail -f /tmp/ray/session_latest/logs/ray_client_server_*
docker exec ray-standalone-worker tail -f /tmp/ray/session_latest/logs/raylet_*
```

## 📊 **Step 5: Monitoring & Verification**

### **5.1 Cluster Status**
```bash
# Check all nodes
docker node ls

# Check services
docker stack services ray-cluster

# Check containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### **5.2 Ray Dashboard**
- **URL**: http://192.168.1.100:8265
- **Nodes Tab**: Should show head + remote worker
- **Actors Tab**: Should show inference actors
- **Resources Tab**: Should show CPU/memory usage

### **5.3 Log Monitoring**
```bash
# Head node logs
docker service logs ray-cluster_ray-head -f

# Remote worker logs
docker logs ray-standalone-worker -f

# Client logs (when testing)
docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest
```

## 🧹 **Step 6: Cleanup**

### **6.1 Stop Remote Worker**
```bash
# On remote worker machine
docker stop ray-standalone-worker
docker rm ray-standalone-worker
```

### **6.2 Stop Head Cluster**
```bash
# On head node machine
./cleanup.sh
```

## 🎯 **Key Testing Points**

1. **✅ Port Configuration**: All ports are configured in code
2. **✅ Network Setup**: Only need to open firewall ports
3. **✅ Service Discovery**: Ray handles its own networking
4. **✅ Cross-Machine Communication**: Direct TCP/IP connection
5. **✅ Dashboard Monitoring**: Real-time cluster status
6. **✅ Interactive Testing**: Full prompt processing demo

## 🚀 **Success Criteria**

- ✅ Head node starts and exposes all ports
- ✅ Remote worker connects to head node
- ✅ Ray dashboard shows both nodes
- ✅ Interactive client can process prompts
- ✅ Prompts are processed on remote worker
- ✅ Response shows correct worker node information

The setup is fully automated - no manual console configuration needed! 🎉 