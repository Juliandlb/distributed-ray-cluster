# 🚀 Multi-Machine Ray Cluster Setup

This guide shows how to set up a distributed Ray cluster across multiple machines using Docker Swarm.

## 🎯 Overview

- **Manager Node**: Runs the Ray cluster coordinator and manages the Docker Swarm
- **Worker Nodes**: Join the Swarm and run Ray workers for inference
- **Secure Communication**: Uses Docker Swarm overlay network for encrypted communication

## 🖥️ Step 1: Start the Cluster (Manager Node)

On your manager machine:

```bash
# Clone the repository
git clone https://github.com/Juliandlb/distributed-ray-cluster.git
cd distributed-ray-cluster/ray_cluster

# Start the cluster
./start_cluster.sh
```

**Expected Output:**
```
🚀 Starting Ray Cluster (Head Node)
==================================
📍 Public IP: <your-public-ip>
🔧 Initializing Docker Swarm...
🔨 Building and deploying Ray cluster...
⏳ Waiting for services to be ready...

🎯 CLUSTER READY FOR INTERNET WORKERS!
======================================
📍 Public IP: <your-public-ip>
🔌 Ray Port: 6379
📊 Dashboard: http://<your-public-ip>:8265

🔑 Join Token: <swarm-join-token>

🔗 To connect a remote worker, run this on the remote machine:
   ./join_swarm_worker.sh

After joining, scale workers from the manager (this node):
   docker service scale ray-cluster_ray-worker=<num>

✅ Cluster is running and ready for remote workers!
```

## 🤖 Step 2: Join Remote Workers

On each remote worker machine:

```bash
# Clone the repository (if not already done)
git clone https://github.com/Juliandlb/distributed-ray-cluster.git
cd distributed-ray-cluster/ray_cluster

# Run the automated join script
./join_swarm_worker.sh
```

**Expected Output:**
```
🤖 Joining Docker Swarm Cluster
===============================
📍 Manager IP: 52.224.243.185
🔑 Join Token: SWMTKN-1-...
🔍 Testing connectivity to manager node...
✅ Connectivity test passed!

🔗 Joining Docker Swarm cluster...
This node joined a swarm as a worker.

✅ Successfully joined the Docker Swarm cluster!
```

**Alternative: Direct Ray Connection**
If Docker Swarm doesn't work due to network restrictions, you can use direct Ray connection:
```bash
./setup_laptop_worker.sh
```

## 🛠️ Step 3: Scale Workers (from Manager)

Back on the manager node:

```bash
# Scale to 3 workers (or however many you want)
docker service scale ray-cluster_ray-worker=3

# Check the status
docker stack services ray-cluster
docker node ls
```

## 🎮 Step 4: Test the Cluster

On the manager node:

```bash
# Run the interactive demo
docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest
```

**Example Interaction:**
```
🎮 [REAL INTERACTIVE PROMPTS] Distributed Ray Cluster Client
============================================================
🔗 Connecting to Ray cluster...
✅ Connected to Ray cluster
🎯 [COORDINATOR] Looking for prompt coordinator...
✅ Found prompt coordinator
🤖 Available inference actors: 3

🎮 [INTERACTIVE MODE] Type your prompts below
============================================

🤖 [PROMPT] hello world
📤 [SENDING] Sending to coordinator...
📥 [RESPONSE] Received in 2.34s

💬 [RESPONSES]
   ✅ Actor 0 (gpt2)
      Worker Node #1: worker-machine-1 (<ip>)
      Processing time: 2.34s
      Response: Hello world! How can I help you today?

🎯 [ANSWERED BY] Worker Node #1
   Hostname: worker-machine-1 (<ip>)
   Model: gpt2
   Processing time: 2.34s
```

## 📊 Step 5: Monitor the Cluster

### Ray Dashboard
- **URL**: http://<manager-public-ip>:8265
- **Shows**: All nodes, actors, resources, and cluster status

### Docker Swarm Commands
```bash
# Check all nodes
docker node ls

# Check services
docker stack services ray-cluster

# Check service logs
docker service logs ray-cluster_ray-head
docker service logs ray-cluster_ray-worker

# Check resource usage
docker stats
```

## 🔧 Troubleshooting

### If a worker can't join the Swarm:
1. **Use the automated script:**
   ```bash
   ./join_swarm_worker.sh
   ```
   The script will test connectivity and provide troubleshooting steps.

2. **Manual troubleshooting:**
   ```bash
   # Check network connectivity:
   ping 52.224.243.185
   telnet 52.224.243.185 2377
   ```

3. **Check firewall settings:**
   ```bash
   # On all nodes, open required ports:
   sudo ufw allow 2377/tcp    # Swarm management
   sudo ufw allow 7946/tcp    # Swarm communication
   sudo ufw allow 7946/udp    # Swarm communication
   sudo ufw allow 4789/udp    # Overlay network
   sudo ufw allow 6379/tcp    # Ray
   sudo ufw allow 8265/tcp    # Dashboard
   ```

4. **Check Docker status:**
   ```bash
   sudo systemctl status docker
   docker info | grep Swarm
   ```

5. **Alternative: Use direct Ray connection:**
   ```bash
   ./setup_laptop_worker.sh
   ```

### If workers don't appear in Ray dashboard:
1. **Wait for initialization** (can take 1-2 minutes)
2. **Check service logs:**
   ```bash
   docker service logs ray-cluster_ray-worker
   ```
3. **Scale workers again:**
   ```bash
   docker service scale ray-cluster_ray-worker=0
   docker service scale ray-cluster_ray-worker=3
   ```

### If the cluster is slow:
1. **Check resource usage:**
   ```bash
   docker stats
   ```
2. **Scale down if needed:**
   ```bash
   docker service scale ray-cluster_ray-worker=1
   ```

## 🧹 Cleanup

### Remove the entire cluster:
```bash
# On manager node
./cleanup.sh
```

### Remove a worker node:
```bash
# On worker node
docker swarm leave
```

## 🚀 Advanced Features

### Scale Workers Dynamically
```bash
# Scale to 5 workers
docker service scale ray-cluster_ray-worker=5

# Scale to 1 worker
docker service scale ray-cluster_ray-worker=1
```

### Add More Worker Nodes
1. Install Docker on a new machine
2. Join the Swarm using the same token
3. Scale the service to use the new node

### Monitor in Real-Time
```bash
# Watch service status
watch -n 5 'docker stack services ray-cluster'

# Follow logs
docker service logs -f ray-cluster_ray-worker
```

## 🎯 Success Criteria

✅ **You should see:**
1. All worker nodes appear in `docker node ls`
2. Ray workers running on multiple machines
3. Ray dashboard shows all nodes
4. Interactive prompts are processed across different machines
5. Response shows different worker hostnames/IPs

**Your multi-machine Ray cluster is now ready! 🎉** 