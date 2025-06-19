# Distributed Ray Cluster for LLM Inference

A containerized distributed Ray cluster for running large language model inference across multiple nodes.

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

## Quick Start

### For Laptops (Limited Resources)

If you're running on a laptop with limited RAM/CPU:

```bash
# Use the laptop-optimized startup script
./scripts/start_laptop.sh
```

This will:
- Use only 2GB memory per container
- Load only the smallest model (tiny-gpt2)
- Limit CPU usage to 2 cores per container
- Provide resource monitoring and warnings

### For Desktops/Servers (Full Resources)

```bash
# Build all Docker images
./build.sh

# Start with Docker Compose
docker-compose up -d
```

## System Requirements

### Minimum (Laptop Mode)
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
    object_store_memory: 1000000000  # 1GB
    num_cpus: 4
    include_dashboard: true
    log_to_driver: true
    logging_level: INFO

models:
  preload: ["tiny-gpt2", "distilbert", "flan-t5-small"]
  cache_dir: "/app/models"
```

### Worker Node Configuration (`config/worker_config.yaml`)

```yaml
ray:
  worker:
    head_address: ${RAY_HEAD_ADDRESS}
    port: 0  # Auto-assign
    object_store_memory: 1000000000
    num_cpus: 4
    num_gpus: ${CUDA_VISIBLE_DEVICES:-0}

models:
  preload: ["tiny-gpt2", "distilbert", "flan-t5-small"]
  auto_load: true
```

## Adding Worker Nodes

### Method 1: Docker Compose

Add more worker services to `docker-compose.yml`:

```yaml
ray-worker-3:
  build:
    context: .
    dockerfile: Dockerfile.worker
  environment:
    - RAY_HEAD_ADDRESS=ray-head:6379
    - CUDA_VISIBLE_DEVICES=2
  depends_on:
    - ray-head
  networks:
    - ray-cluster
```

### Method 2: Manual Docker Run

```bash
# On any machine that can reach the head node
docker run -d \
  --name ray-worker-new \
  -e RAY_HEAD_ADDRESS=<head-node-ip>:6379 \
  -e CUDA_VISIBLE_DEVICES=0 \
  ray-cluster-worker:latest
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
        image: ray-cluster-worker:latest
        env:
        - name: RAY_HEAD_ADDRESS
          value: "ray-head-service:6379"
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RAY_HEAD_ADDRESS` | Head node address (required for workers) | - |
| `CUDA_VISIBLE_DEVICES` | GPU devices to use | `0` |
| `RAY_DISABLE_DEDUP` | Disable log deduplication | `1` |
| `PYTHONUNBUFFERED` | Unbuffered Python output | `1` |

## Available Models

The cluster supports these pre-configured models:

- **tiny-gpt2**: Small GPT-2 model for text generation (fastest, ~50MB)
- **distilbert**: DistilBERT for masked language modeling (~260MB)
- **flan-t5-small**: Small T5 model for text-to-text generation (~300MB)

**Note**: Laptop mode only loads `tiny-gpt2` to save memory.

## Monitoring and Debugging

### View Cluster Status

```bash
# Check running containers
docker ps

# View logs
docker-compose logs -f ray-head
docker-compose logs -f ray-worker-1

# Access Ray dashboard
open http://localhost:8265
```

### Health Checks

Each container includes health checks that verify Ray processes are running:

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Resource Monitoring

```bash
# Monitor system resources
htop
# or
top

# Monitor Docker resources
docker stats
```

### Troubleshooting

1. **Worker can't connect to head node**:
   - Verify `RAY_HEAD_ADDRESS` is correct
   - Check network connectivity
   - Ensure head node is running and healthy

2. **Models not loading**:
   - Check available memory
   - Verify model names in configuration
   - Check logs for download errors

3. **GPU not detected**:
   - Verify CUDA installation in container
   - Check `CUDA_VISIBLE_DEVICES` environment variable
   - Ensure GPU drivers are compatible

4. **Out of memory errors**:
   - Use laptop mode: `./scripts/start_laptop.sh`
   - Close other applications
   - Reduce number of worker nodes
   - Load fewer models

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