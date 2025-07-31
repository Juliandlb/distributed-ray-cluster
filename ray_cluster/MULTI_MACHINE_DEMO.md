# 🚀 Multi-Machine Ray Cluster Setup

This guide shows how to set up a distributed Ray cluster across multiple machines using **Direct Ray Connection** (bypassing Docker Swarm for better compatibility).

## 🎯 Goal of the Demo

The primary goal of this demonstration is to illustrate a distributed computing setup where a central **head node** (running on a VM) coordinates tasks for one or more **worker nodes** (including a remote laptop). This setup is designed to showcase how a resource-intensive task, such as responding to a prompt, can be offloaded from a local machine to a more powerful, distributed cluster.

In this demo, you will:

1.  **Set up a Ray cluster:** A head node on a VM will form the core of the cluster.
2.  **Connect a remote worker:** Your laptop will join the cluster as a worker node.
3.  **Run a distributed application:** You will send a prompt to the head node, which will then delegate the processing of that prompt to the connected worker nodes.
4.  **Observe distributed computing in action:** You will see the response from the worker node, demonstrating that the task was successfully offloaded and executed remotely.

This setup provides a practical example of how to leverage distributed computing to scale applications and perform intensive computations on remote resources.

## 🎯 Overview

##  Architecture Overview

This demo uses a simple, direct-connection architecture:

- **Head Node (Azure VM):** This is the central coordinator of the Ray cluster. It runs the Ray head process, manages the cluster's state, and orchestrates the distribution of tasks. It does *not* run a Docker Swarm, simplifying the setup and avoiding potential networking complexities.
- **Worker Nodes (Laptop/Remote):** These are the machines that perform the actual computations. They connect directly to the head node using Ray's native TCP communication, without needing to be part of a Docker Swarm. This allows for a more flexible and heterogeneous cluster.
- **Client:** A client application connects to the head node to submit tasks (in this case, prompts) and retrieve results.

This direct-connection model is ideal for scenarios where you want to quickly and easily connect remote machines to a central cluster without the overhead of a more complex container orchestration system.

## 🖥️ Step 1: Start the Cluster (Head Node)

On your Azure VM:

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
🔧 Initializing Ray cluster...
🔨 Building and deploying Ray cluster...
⏳ Waiting for services to be ready...

🎯 CLUSTER READY FOR REMOTE WORKERS!
======================================
📍 Public IP: <your-public-ip>
🔌 Ray Port: 6379
📊 Dashboard: http://<your-public-ip>:8265
🔌 Ray Client Port: 10001

✅ Cluster is running and ready for remote workers!
```

## 🤖 Step 2: Join Remote Workers

On each remote worker machine (e.g., your laptop):

```bash
# Clone the repository (if not already done)
git clone https://github.com/Juliandlb/distributed-ray-cluster.git
cd distributed-ray-cluster/ray_cluster

# Run the automated join script
./start_remote_worker_direct.sh <HEAD_NODE_IP>
```

**Example:**
```bash
./start_remote_worker_direct.sh 52.224.243.185
```

**Expected Output:**
```
🤖 Starting Direct Ray Worker
============================
📍 Worker IP: <your-laptop-ip>
🔗 Connecting to Head: 52.224.243.185:6379
🔨 Building worker image...
🚀 Starting direct worker container...
✅ Ray worker node joined successfully!
```

## 🎮 Step 3: Test the Cluster

## How it Works: The Journey of a Prompt

When you submit a prompt to the cluster, it goes through the following steps:

1.  **Client Submission:** The interactive client connects to the Ray cluster via the head node's client port (10001).
2.  **Coordinator on Head Node:** The client looks for a "prompt coordinator" actor running on the head node. This actor is responsible for receiving prompts and distributing them to available workers.
3.  **Task Distribution:** The coordinator forwards the prompt to one of the available "inference actors" running on the worker nodes.
4.  **Worker Execution:** The inference actor on the worker node receives the prompt, processes it (in a real-world scenario, this would involve a machine learning model), and generates a response.
5.  **Response Return:** The response is sent back to the coordinator, which then forwards it to the client.

This entire process is orchestrated by Ray, which handles the communication, task scheduling, and data serialization between the different components.

On the head node (VM):

```bash
# Run the simple demo to verify cluster status
docker build -f Dockerfile.simple -t ray-cluster-simple:latest .
docker run --rm --network host ray-cluster-simple:latest
```

**Expected Output:**
```
🔗 Connecting to Ray cluster...
✅ Connected to Ray cluster
🎯 Looking for prompt coordinator...
✅ Found prompt coordinator
🤖 Available inference actors: 0

⚠️  No inference actors available.
This is expected if no worker nodes are running inference actors.
The cluster is working correctly - the head node is running.

📊 Cluster has X nodes:
   🟢 Head Node (unknown)
      IP: unknown
      Actors: 0
   🔴 Worker Node #1 (unknown)
      IP: unknown
      Actors: 0

✅ Cluster is working! The head node is running correctly.
To add inference actors, you need worker nodes running inference actors.
```

## 🛠️ Step 4: Run Interactive Demo (When Workers Are Available)

When worker nodes are successfully running inference actors:

```bash
# Run the interactive demo
docker build -f Dockerfile.client -t ray-cluster-client:latest .
docker run --rm -it --network host ray-cluster-client:latest
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
- **URL**: http://<head-node-public-ip>:8265
- **Shows**: All nodes, actors, resources, and cluster status

### Ray Client Commands
```bash
# Check cluster status from head node
docker run --rm --network host ray-cluster-simple:latest

# Check worker logs
docker logs ray-direct-worker
```

## 🔧 Troubleshooting

### If a worker can't join the cluster:
1. **Check network connectivity:**
   ```bash
   ping <head-node-ip>
   telnet <head-node-ip> 6379
   ```

2. **Check firewall settings:**
   ```bash
   # On head node, ensure ports are open:
   sudo ufw allow 6379/tcp    # Ray
   sudo ufw allow 8265/tcp    # Dashboard
   sudo ufw allow 10001/tcp   # Ray Client
   ```

3. **Check Docker networking:**
   ```bash
   # If Docker networking fails, try:
   docker run --rm --network host --name ray-direct-worker \
     -e RAY_HEAD_ADDRESS=<head-ip>:6379 \
     ray-cluster-worker:latest
   ```

### If workers don't create inference actors:
1. **Check worker logs:**
   ```bash
   docker logs ray-direct-worker
   ```

2. **Restart worker with host networking:**
   ```bash
   docker rm -f ray-direct-worker
   ./start_remote_worker_direct.sh <head-ip>
   ```

### If the cluster is slow:
1. **Check resource usage:**
   ```bash
   docker stats
   ```

2. **Scale down if needed:**
   ```bash
   # Stop workers
   docker stop ray-direct-worker
   ```

## 🧹 Cleanup

### Remove the entire cluster:
```bash
# On head node
./cleanup.sh
```

### Remove a worker node:
```bash
# On worker node
docker stop ray-direct-worker && docker rm ray-direct-worker
```

## 🚀 Current Status

✅ **Working Components:**
- Head node (Azure VM) running Ray cluster
- Ray Client connection (port 10001)
- Prompt coordinator available
- Cluster status monitoring
- Simple demo script working

⚠️ **Known Issues:**
- Docker networking issues on some laptops prevent worker containers from starting
- Workers may join cluster but not create inference actors due to networking constraints

🔧 **Workarounds:**
- Use `--network host` for worker containers
- Run workers on machines without Docker networking issues
- Use the simple demo to verify cluster functionality

## 🎯 Success Criteria

✅ **You should see:**
1. Head node running Ray cluster
2. Ray Client connecting successfully
3. Prompt coordinator available
4. Simple demo showing cluster status
5. Worker nodes joining (when networking works)

**Your multi-machine Ray cluster is now ready! 🎉** 