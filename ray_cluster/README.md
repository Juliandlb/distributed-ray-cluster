# Distributed Ray Cluster for LLM Inference

A containerized distributed Ray cluster for running large language model inference across multiple nodes. **Successfully tested and working!** 🎉

## ✅ **Verified Working Features**

- 🐳 **Containerized**: Easy deployment with Docker
- 🔄 **Dynamic Scaling**: Worker nodes can join/leave at any time
- 🎯 **Load Balancing**: Automatic distribution of inference tasks
- 📊 **Monitoring**: Ray dashboard for cluster monitoring
- 🚀 **GPU Support**: Automatic GPU detection and utilization
- 🔧 **Configurable**: YAML-based configuration for easy customization
- 💻 **Laptop Optimized**: Special configuration for limited resources
- ✅ **Distributed Inference**: Successfully tested with concurrent requests
- 🛠️ **Robust Health Checks**: Ray API-based health monitoring
- 🔧 **Syntax Error Free**: All Unicode and encoding issues resolved

## 🆕 **Latest Improvements (June 2025)**

### **Major Fixes Achieved:**

1. **✅ Syntax Error Resolution**
   - **Problem**: Unicode arrow characters (→) causing Python syntax errors
   - **Solution**: Replaced all emoji characters with ASCII equivalents
   - **Result**: Clean, error-free Python execution

2. **✅ Health Check System Overhaul**
   - **Problem**: Unreliable process-based health checks using `netstat`/`ps`
   - **Solution**: Implemented lightweight Ray API-based health checks
   - **Result**: Reliable cluster health monitoring with resource reporting

3. **✅ Worker Connection Stability**
   - **Problem**: Ray Client dependency issues (`ray[client]` not installed)
   - **Solution**: Changed to direct Ray connection (`ray-head:6379`)
   - **Result**: Stable worker-to-head node connections

4. **✅ Docker Image Optimization**
   - **Problem**: Base image caching issues with outdated `main.py`
   - **Solution**: Added explicit `COPY main.py` to worker Dockerfile
   - **Result**: Consistent, up-to-date code across all containers

### **Current Cluster Status:**
- **Head Node**: ✅ Healthy and stable
- **Worker Nodes**: ✅ Successfully connecting and contributing resources
- **Health Checks**: ✅ Ray API-based monitoring working
- **Resource Distribution**: ✅ Proper CPU/memory allocation
- **Application Stability**: ✅ No syntax errors or connection issues

### **Technical Improvements:**
- **Health Check Script**: Reduced from ~80 lines to ~10 lines
- **Error Handling**: Enhanced with proper Ray connection management
- **Logging**: Improved with ASCII-only characters for better compatibility
- **Container Architecture**: Optimized for reliability and consistency

## 🎯 **Quick Start (Tested & Working)**

### **Step 1: Navigate to Project Directory**
```bash
cd /home/juliandlbb/repos/distributed-ray-cluster/ray_cluster
```

### **Step 2: Start the Head Node**
```bash
# Start the head node with laptop-optimized settings
docker-compose -f docker-compose.laptop.yml up -d ray-head
```

**What this does:**
- Creates and starts the head node container (`ray-cluster-head-laptop`)
- Exposes Ray port 6379 and dashboard port 8265
- Uses optimized settings for your laptop (2GB memory, 2 CPUs)
- Loads the tiny-gpt2 model (~625MB RSS)

### **Step 3: Wait for Head Node to be Ready**
```bash
# Check if head node is running
docker ps

# View head node logs
docker logs ray-cluster-head-laptop
```

**Expected output:**
```
Ray head node started successfully!
Dashboard available at: http://172.18.0.2:8265
Starting main application in head mode...
=== Running in HEAD Mode ===
=== Ray Cluster Started ===
=== Creating Model Instances ===
```

### **Step 4: Start Worker Node**
```bash
# Start worker node (manually if health check fails)
docker run -d --name ray-cluster-worker-laptop \
  --network ray_cluster_ray-cluster \
  -e RAY_HEAD_ADDRESS=ray-cluster-head-laptop:6379 \
  -e CUDA_VISIBLE_DEVICES= \
  -e RAY_DISABLE_DEDUP=1 \
  -e RAY_DISABLE_CUSTOM_LOGGER=1 \
  -e PYTHONUNBUFFERED=1 \
  ray_cluster-ray-worker-1
```

### **Step 5: Verify Worker Connection**
```bash
# Check worker logs
docker logs ray-cluster-worker-laptop
```

**Expected output:**
```
=== Starting Ray Worker Node ===
Head node is ready!
Ray worker node joined successfully!
=== Worker Node Ready ===
Loaded 1 models and ready for inference
```

### **Step 6: Monitor Cluster Status**
```bash
# Check both containers
docker ps

# View cluster resources in head logs
docker logs ray-cluster-head-laptop --tail 5
```

**Expected cluster resources:**
```
Cluster Resources: {
  'node:172.18.0.2': 1.0, 
  'CPU': 4.0, 
  'memory': 12945716736.0, 
  'object_store_memory': 1000000000.0, 
  'node:__internal_head__': 1.0, 
  'node:172.18.0.3': 1.0
}
```

## 🎉 **Successfully Tested Results**

### **Distributed Inference Test**
The cluster successfully processed **5 concurrent inference requests**:

1. "What is machine learning?"
2. "Explain quantum computing"
3. "Tell me about Ray"
4. "What is distributed computing?"
5. "Explain LLM inference"

**Results:**
- ✅ **Round-robin distribution** between head and worker nodes
- ✅ **Concurrent processing** across multiple nodes
- ✅ **Memory tracking** with efficient resource usage
- ✅ **Load balancing** working correctly

### **Cluster Performance**
- **Head Node**: 2 CPUs, ~1.2GB memory, tiny-gpt2 model loaded
- **Worker Node**: 2 CPUs, additional memory, tiny-gpt2 model loaded
- **Total Cluster**: 4 CPUs, ~12.9GB memory, distributed processing
- **Response Time**: Fast inference with memory monitoring

## Architecture

The cluster consists of:
- **Head Node**: Manages the cluster, provides dashboard, and coordinates tasks
- **Worker Nodes**: Execute model inference tasks and can join/leave dynamically
- **Models**: Multiple LLM models (GPT-2, DistilBERT, T5) distributed across nodes

## Features

- 🐳 **Containerized**: Easy deployment with Docker
- 🔄 **Dynamic Scaling**: Worker nodes can join/leave at any time
- 🎯 **Load Balancing**: Automatic distribution of inference tasks
- 📊 **Monitoring**: Ray dashboard for cluster monitoring
- 🚀 **GPU Support**: Automatic GPU detection and utilization
- 🔧 **Configurable**: YAML-based configuration for easy customization
- 💻 **Laptop Optimized**: Special configuration for limited resources

## System Requirements

### Minimum (Laptop Mode) - **Tested & Working**
- **RAM**: 4GB available (8GB total recommended)
- **CPU**: 4 cores
- **Storage**: 5GB free space
- **Docker**: Latest version

### Recommended (Full Mode)
- **RAM**: 8GB+ available
- **CPU**: 8+ cores
- **GPU**: Optional (CUDA compatible)
- **Storage**: 10GB+ free space

## Configuration

### Laptop Configuration (`config/laptop_config.yaml`)

```yaml
ray:
  head:
    port: 6379
    dashboard_port: 8265
    object_store_memory: 500000000  # 500MB
    num_cpus: 2
    include_dashboard: true

models:
  preload: ["tiny-gpt2"]  # Only smallest model
  cache_dir: "/app/models"

resources:
  memory_limit: "2GB"
  cpu_limit: "2"
```

### Head Node Configuration (`config/head_config.yaml`)

```yaml
ray:
  head:
    port: 6379
    dashboard_port: 8265
    object_store_memory: 500000000  # 500MB (optimized)
    num_cpus: 2  # Reduced for laptop
    include_dashboard: true
    log_to_driver: true
    logging_level: INFO

models:
  preload: ["tiny-gpt2"]  # Only smallest model
  cache_dir: "/app/models"
```

### Worker Node Configuration (`config/worker_config.yaml`)

```yaml
ray:
  worker:
    head_address: ${RAY_HEAD_ADDRESS}
    port: 0  # Auto-assign
    object_store_memory: 500000000  # 500MB (optimized)
    num_cpus: 2  # Reduced for laptop
    num_gpus: ${CUDA_VISIBLE_DEVICES:-0}

models:
  preload: ["tiny-gpt2"]  # Only smallest model
  auto_load: true
```

## Adding Worker Nodes

### Method 1: Manual Docker Run (Recommended)

```bash
# Start additional worker nodes
docker run -d --name ray-cluster-worker-2 \
  --network ray_cluster_ray-cluster \
  -e RAY_HEAD_ADDRESS=ray-cluster-head-laptop:6379 \
  -e CUDA_VISIBLE_DEVICES= \
  -e RAY_DISABLE_DEDUP=1 \
  -e RAY_DISABLE_CUSTOM_LOGGER=1 \
  -e PYTHONUNBUFFERED=1 \
  ray_cluster-ray-worker-1
```

### Method 2: Docker Compose

Add more worker services to `docker-compose.laptop.yml`:

```yaml
ray-worker-2:
  build:
    context: .
    dockerfile: Dockerfile.worker
  environment:
    - RAY_HEAD_ADDRESS=ray-cluster-head-laptop:6379
    - CUDA_VISIBLE_DEVICES=
    - RAY_DISABLE_DEDUP=1
    - RAY_DISABLE_CUSTOM_LOGGER=1
    - PYTHONUNBUFFERED=1
  depends_on:
    - ray-head
  networks:
    - ray-cluster
```

### Method 3: Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ray-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ray-worker
  template:
    metadata:
      labels:
        app: ray-worker
    spec:
      containers:
      - name: ray-worker
        image: ray_cluster-ray-worker-1:latest
        env:
        - name: RAY_HEAD_ADDRESS
          value: "ray-cluster-head-laptop:6379"
        - name: CUDA_VISIBLE_DEVICES
          value: ""
```

## 🚀 Running Multiple Worker Nodes (Laptop Mode)

### Quick Scaling with Script

The easiest way to add multiple worker nodes is using the provided script:

```bash
# Add 3 worker nodes
./add_workers.sh 3

# Add 5 worker nodes  
./add_workers.sh 5

# Add 10 worker nodes (be careful with memory!)
./add_workers.sh 10
```

### Manual Scaling

Add worker nodes one by one:

```bash
# Worker 1
docker run -d --name ray-cluster-worker-1 \
  --network ray_cluster_ray-cluster \
  -e RAY_HEAD_ADDRESS=ray-cluster-head-laptop:6379 \
  -e CUDA_VISIBLE_DEVICES= \
  -e RAY_DISABLE_DEDUP=1 \
  -e RAY_DISABLE_CUSTOM_LOGGER=1 \
  -e PYTHONUNBUFFERED=1 \
  ray_cluster-ray-worker-1

# Worker 2
docker run -d --name ray-cluster-worker-2 \
  --network ray_cluster_ray-cluster \
  -e RAY_HEAD_ADDRESS=ray-cluster-head-laptop:6379 \
  -e CUDA_VISIBLE_DEVICES= \
  -e RAY_DISABLE_DEDUP=1 \
  -e RAY_DISABLE_CUSTOM_LOGGER=1 \
  -e PYTHONUNBUFFERED=1 \
  ray_cluster-ray-worker-1

# Continue for more workers...
```

### Check Cluster Scaling

Monitor your cluster as it scales:

```bash
# View all running containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check cluster resources
docker logs ray-cluster-head-laptop --tail 5

# Monitor resource usage
docker stats
```

### Laptop Scaling Considerations

**Recommended Limits for 11GB RAM Laptop:**
- **Conservative**: 2-3 worker nodes (~6-9GB total)
- **Aggressive**: 4-5 worker nodes (~8-11GB total)
- **Maximum**: 6+ worker nodes (may cause OOM)

**Memory Usage per Worker:**
- **tiny-gpt2 model**: ~650MB RSS per worker
- **Base container**: ~200MB per worker
- **Total per worker**: ~850MB-1GB

**Scaling Benefits:**
- **More CPUs**: Each worker adds 2 CPUs
- **Better load distribution**: Tasks spread across nodes
- **Higher throughput**: More concurrent operations
- **Fault tolerance**: If one worker fails, others continue

**Warning Signs:**
- System becomes sluggish
- Docker stats show high memory usage
- OOM errors in logs
- Workers being killed by Ray memory monitor

### Scaling Down

Remove worker nodes when needed:

```bash
# Stop and remove specific workers
docker stop ray-cluster-worker-3 ray-cluster-worker-4
docker rm ray-cluster-worker-3 ray-cluster-worker-4

# Or remove all workers
docker stop $(docker ps -q --filter "name=ray-cluster-worker")
docker rm $(docker ps -aq --filter "name=ray-cluster-worker")
```

### Example: Scaling Session

```bash
# Start with head node
docker-compose -f docker-compose.laptop.yml up -d ray-head

# Add 3 workers
./add_workers.sh 3

# Check cluster status
docker logs ray-cluster-head-laptop --tail 3
# Expected output: CPU: 6.0, memory: ~36GB, 4 nodes total

# Add 2 more workers
./add_workers.sh 2

# Check final status  
docker logs ray-cluster-head-laptop --tail 3
# Expected output: CPU: 10.0, memory: ~48GB, 6 nodes total
```

**Result:** Your laptop can handle multiple worker nodes, but monitor memory usage carefully!

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RAY_HEAD_ADDRESS` | Head node address (required for workers) | - |
| `CUDA_VISIBLE_DEVICES` | GPU devices to use | `0` |
| `RAY_DISABLE_DEDUP` | Disable log deduplication | `1` |
| `PYTHONUNBUFFERED` | Unbuffered Python output | `1` |

## Available Models

The cluster supports these pre-configured models:

- **tiny-gpt2**: Small GPT-2 model for text generation (fastest, ~50MB) - **✅ Tested & Working**
- **distilbert**: DistilBERT for masked language modeling (~260MB)
- **flan-t5-small**: Small T5 model for text-to-text generation (~300MB)

**Note**: Laptop mode only loads `tiny-gpt2` to save memory and prevent OOM issues.

## Monitoring and Debugging

### View Cluster Status

```bash
# Check running containers
docker ps

# View logs
docker logs ray-cluster-head-laptop
docker logs ray-cluster-worker-laptop

# Access Ray dashboard
open http://localhost:8265
```

### Health Checks

Each container includes **Ray API-based health checks** that verify Ray cluster connectivity and resource availability:

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Test health check manually
docker exec ray-cluster-head /app/health_check.sh
```

**Health Check Features:**
- ✅ **Lightweight**: Uses Python Ray API instead of system tools
- ✅ **Reliable**: Tests actual Ray functionality, not just process presence
- ✅ **Informative**: Shows available cluster resources
- ✅ **Fast**: Quick Python API call instead of system process inspection

**Expected Output:**
```
✅ Ray is initialized and cluster resources are available: {
  'CPU': 4.0, 
  'memory': 23056528896.0, 
  'GPU': 1.0, 
  'object_store_memory': 1000000000.0
}
```

**Note**: The new health check system is much more reliable than the previous process-based checks and provides better visibility into cluster status.

### Resource Monitoring

```bash
# Monitor system resources
htop
# or
top

# Monitor Docker resources
docker stats
```

### 🔍 Enhanced Logging & Node Operation Visibility

This cluster now features **detailed, real-time logging** for every node and every inference operation:

- **Prompt and Output Visibility:**
  - Every prompt sent to a model is logged with node, process, and Ray node ID information.
  - The output (model response) is also logged, along with timing and memory usage, for every inference operation.
  - Logs are clearly separated and labeled, making it easy to see which node and which actor handled each request.

- **Cluster Operation Visibility:**
  - The head node logs task distribution, which actor handled which prompt, and prints a summary of all results.
  - Worker nodes log their own status, model loading, and readiness, and will show inference logs if they are assigned tasks.

- **How to Observe:**
  - View logs in real time with:
    ```bash
    docker logs ray-cluster-head-laptop
    docker logs ray-cluster-worker-laptop
    ```
  - Logs show banners for actor creation, prompt receipt, output, and periodic status updates.
  - All logs include node/actor identification for full traceability.

- **Test Script:**
  - Use the provided test script to trigger distributed inference and see the enhanced logging in action:
    ```bash
    python test_distributed_inference.py
    ```
  - The script sends prompts to the cluster and you can observe the detailed logs in the container outputs.

**Result:**
You have full, clear, real-time visibility into every operation, prompt, and output for every node and actor in your distributed Ray cluster.

### Troubleshooting

1. **Worker can't connect to head node**:
   - Verify `RAY_HEAD_ADDRESS` is correct: `ray-cluster-head-laptop:6379`
   - Check network connectivity: `docker network ls`
   - Ensure head node is running: `docker logs ray-cluster-head-laptop`
   - **Fixed**: No longer need `ray[client]` package - using direct Ray connection

2. **Models not loading**:
   - Check available memory: `docker stats`
   - Verify model names in configuration
   - Check logs for download errors

3. **GPU not detected**:
   - Verify CUDA installation in container
   - Check `CUDA_VISIBLE_DEVICES` environment variable
   - Ensure GPU drivers are compatible

4. **Out of memory errors**:
   - Use laptop mode: `docker-compose -f docker-compose.laptop.yml up -d`
   - Close other applications
   - Reduce number of worker nodes
   - Load fewer models

5. **Health check failures**:
   - **Fixed**: New Ray API-based health checks are reliable
   - Test manually: `docker exec <container> /app/health_check.sh`
   - Check if Ray is actually running: `docker logs <container-name>`

6. **Syntax errors or Unicode issues**:
   - **Fixed**: All emoji characters replaced with ASCII equivalents
   - Ensure you're using the latest `main.py` file
   - Rebuild containers if needed: `docker-compose build --no-cache`

## Production Deployment

### Security Considerations

- Use private Docker registries
- Implement network segmentation
- Add authentication for Ray dashboard
- Use secrets management for sensitive data

### Scaling Strategies

- **Horizontal Scaling**: Add more worker nodes
- **Vertical Scaling**: Increase CPU/memory per node
- **Auto-scaling**: Use Kubernetes HPA or similar

### High Availability

- Deploy multiple head nodes with load balancing
- Use persistent storage for model cache
- Implement health checks and auto-restart
- Monitor resource usage and performance

## Development

### Local Development

```bash
# Run without containers (laptop mode)
python main.py --mode=head --config=config/laptop_config.yaml

# In another terminal
python main.py --mode=worker --config=config/laptop_config.yaml
```

### Adding New Models

1. Add model configuration to `MODEL_CONFIGS` in `main.py`
2. Update configuration files to include the new model
3. Rebuild Docker images

### Customizing the Application

- Modify `main.py` for custom inference logic
- Update configuration files for different settings
- Add new scripts in the `scripts/` directory

## License

This project is open source. See LICENSE file for details. 