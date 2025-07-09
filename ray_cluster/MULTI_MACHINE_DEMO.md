# 🚀 Multi-Machine Ray Cluster Demo

This guide shows how to run a Ray cluster across multiple machines with just one command per machine.

## 🎯 Overview

- **Machine 1 (Head Node)**: Runs the Ray cluster coordinator
- **Machine 2 (Worker Node)**: Runs a Ray worker that connects to the head node
- **Both machines**: Use Docker containers for easy deployment

## 🖥️ Machine 1: Start the Cluster (Head Node)

```bash
# On the head node machine
cd /path/to/ray_cluster
chmod +x start_cluster.sh
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

🔗 To connect a remote worker, run:
   ./start_standalone_worker.sh 192.168.1.100

✅ Cluster is running and ready for remote workers!
```

## 🤖 Machine 2: Join as Remote Worker

```bash
# On the worker machine
cd /path/to/ray_cluster
chmod +x start_standalone_worker.sh
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

## 🎮 Test the Multi-Machine Cluster

```bash
# On the head node machine
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

## 📊 Monitor the Cluster

### Ray Dashboard
- **URL**: http://192.168.1.100:8265
- **Shows**: All nodes (head + remote workers), actors, resources

### Check Worker Status
```bash
# On worker machine
docker logs ray-standalone-worker

# On head machine
docker service logs ray-cluster_ray-head
```

## 🔧 Troubleshooting

### If Worker Can't Connect
1. **Check network connectivity:**
   ```bash
   # On worker machine
   ping 192.168.1.100
   telnet 192.168.1.100 6379
   ```

2. **Check firewall settings:**
   - Ensure port 6379 is open on the head node
   - Ensure ports 12345-12346 are open on the head node

3. **Check Docker network:**
   ```bash
   # On head machine
   docker network ls
   docker network inspect ray-cluster_ray-cluster
   ```

### If Head Node Can't Start
1. **Check Docker Swarm:**
   ```bash
   docker info | grep Swarm
   docker node ls
   ```

2. **Check ports:**
   ```bash
   netstat -tlnp | grep :6379
   ```

## 🧹 Cleanup

### Stop Remote Worker
```bash
# On worker machine
docker stop ray-standalone-worker
docker rm ray-standalone-worker
```

### Stop Head Cluster
```bash
# On head machine
./cleanup.sh
```

## 🎯 Key Features

1. **One Command Setup**: Each machine needs only one command
2. **Standalone Workers**: Remote workers don't need Docker Swarm
3. **Real Multi-Machine**: Workers run on different physical machines
4. **Easy Monitoring**: Ray dashboard shows all nodes
5. **Simple Testing**: Interactive client works from any machine

## 🚀 Next Steps

- Add more worker machines: Run `./start_standalone_worker.sh <HEAD_IP>` on each
- Scale workers: `docker service scale ray-cluster_ray-worker=3`
- Add GPU support: Modify worker Dockerfile and scripts
- Deploy to cloud: Use cloud IP addresses instead of local IPs

The demo is now ready for multi-machine deployment! 🎉 