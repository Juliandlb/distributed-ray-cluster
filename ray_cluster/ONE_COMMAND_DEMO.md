# 🚀 One-Command Ray Cluster Demo

This guide provides a foolproof way to run the distributed Ray cluster demo with minimal effort.

## 📚 Understanding Docker Concepts

### Docker Images vs Containers
- **Images** = Blueprints (like a recipe)
- **Containers** = Running instances (like a cooked meal)
- **Services** = Orchestrated containers (like a restaurant)

### Our Ray Cluster Architecture
```
Images (Blueprints):
├── ray-cluster-head:latest     (1.81GB) - Coordinator
├── ray-cluster-worker:latest   (1.81GB) - Inference Engine  
└── ray-cluster-client:latest   (363MB)  - Interactive Client

Containers (Running):
├── ray-cluster_ray-head.1      - Head node (coordinator)
├── ray-cluster_ray-worker.1    - Worker node (GPT-2 model)
└── ray-cluster_ray-client.1    - Client (interactive prompts)

Services (Orchestrated):
├── ray-cluster_ray-head        - Manages head containers
├── ray-cluster_ray-worker      - Manages worker containers
└── ray-cluster_ray-client      - Manages client containers
```

## 🎯 One-Command Setup

### Prerequisites
```bash
# Ensure Docker is running
docker --version
docker swarm init  # If not already initialized
```

### Complete Demo (Single Command)
```bash
cd /path/to/ray_cluster
./rebuild.sh
```

This single command will:
1. 🧹 Clean up old containers and images
2. 🔨 Build all Docker images (head, worker, client)
3. 🚀 Deploy the cluster with proper memory limits
4. ⏳ Wait for services to be ready
5. ✅ Verify everything is working

## 🔍 Verification Steps

### 1. Check Images (Blueprints)
```bash
docker images | grep ray-cluster
```
Expected output:
```
ray-cluster-worker   latest      [hash]   [time]   1.81GB
ray-cluster-head     latest      [hash]   [time]   1.81GB
ray-cluster-client   latest      [hash]   [time]   363MB
```

### 2. Check Services (Orchestration)
```bash
docker stack services ray-cluster
```
Expected output:
```
ID             NAME                     MODE         REPLICAS   IMAGE                       PORTS
[hash]         ray-cluster_ray-client   replicated   1/1        ray-cluster-client:latest   
[hash]         ray-cluster_ray-head     replicated   1/1        ray-cluster-head:latest     *:6379->6379/tcp, *:8265->8265/tcp, *:10001->10001/tcp, *:10003->10003/tcp, *:12345-12346->12345-12346/tcp
[hash]         ray-cluster_ray-worker   replicated   1/1        ray-cluster-worker:latest   
```

### 3. Check Containers (Running Instances)
```bash
docker ps | grep ray-cluster
```
Expected output:
```
[hash]   ray-cluster-head:latest     "/app/start_head.sh"     [time]   Up [time] (healthy)   [ports]   ray-cluster_ray-head.1.[hash]
[hash]   ray-cluster-worker:latest   "/app/start_worker.sh"   [time]   Up [time] (healthy)   [ports]   ray-cluster_ray-worker.1.[hash]
[hash]   ray-cluster-client:latest   "python real_interac…"   [time]   Up [time]             [ports]   ray-cluster_ray-client.1.[hash]
```

## 🎮 Run the Demo

### Interactive Prompts
```bash
docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest
```

### Expected Demo Output
```
================================================================================
🎮 [REAL INTERACTIVE PROMPTS] Distributed Ray Cluster Client
================================================================================
🔗 Connecting to Ray cluster...
✅ Connected to Ray cluster
🎯 [COORDINATOR] Looking for prompt coordinator...
✅ Found prompt coordinator
🤖 Available inference actors: 1

================================================================================
🎮 [INTERACTIVE MODE] Type your prompts below
================================================================================

🤖 [PROMPT] hello world
📤 [SENDING] Sending to coordinator...
📥 [RESPONSE] Received in 2.34s

💬 [RESPONSES]
   ✅ Actor 0 (gpt2)
      Worker Node #1: [hostname] ([ip])
      Processing time: 2.34s
      Response: Hello world! How can I help you today?

🎯 [ANSWERED BY] Worker Node #1
   Hostname: [hostname] ([ip])
   Model: gpt2
   Processing time: 2.34s

💬 [FINAL RESPONSE] Hello world! How can I help you today?
```

## 🔧 Troubleshooting

### If Services Don't Start
```bash
# Check service logs
docker service logs ray-cluster_ray-head
docker service logs ray-cluster_ray-worker

# Check memory usage
docker stats --no-stream

# Restart with more memory
./rebuild.sh
```

### If Coordinator Not Found
```bash
# Check if coordinator was created
docker service logs ray-cluster_ray-head | grep "Prompt Coordinator"

# Wait for initialization (can take 1-2 minutes)
sleep 60
```

### If Out of Memory
```bash
# Check current memory usage
docker stats --no-stream

# The rebuild.sh script now uses proper memory limits:
# - Head: 2GB limit, 512MB reservation
# - Worker: 3GB limit, 1.5GB reservation
```

## 📊 Monitoring

### Ray Dashboard
- **URL**: http://localhost:8265
- **Shows**: Cluster status, nodes, actors, resources

### Service Status
```bash
# Real-time service monitoring
watch -n 5 'docker stack services ray-cluster'

# Container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Resource Usage
```bash
# Memory and CPU usage
docker stats --no-stream

# Disk usage
docker system df
```

## 🧹 Cleanup

### Remove Everything
```bash
./cleanup.sh
```

### Remove Images Too
```bash
docker rmi ray-cluster-head:latest ray-cluster-worker:latest ray-cluster-client:latest
```

## 🎯 Key Improvements Made

1. **Memory Limits**: Increased to prevent OOM issues
   - Head: 2GB limit (was 1GB)
   - Worker: 3GB limit (was 2GB)

2. **Namespace Fix**: All components now use "default" namespace

3. **Health Checks**: Proper health monitoring for all services

4. **Error Handling**: Better retry logic and error messages

5. **Documentation**: Clear verification steps and troubleshooting

## 🚀 Next Steps

Once the demo is working:
- Scale workers: `docker service scale ray-cluster_ray-worker=3`
- Add custom models: Modify `config/worker_config.yaml`
- Deploy to multiple machines: Follow `README-SWARM.md`

The demo should now be much more reliable and replicable! 🎉 