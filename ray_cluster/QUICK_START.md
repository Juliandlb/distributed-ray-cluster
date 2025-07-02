# 🚀 Quick Start Guide - Ray Cluster

This guide shows you how to quickly build and run the distributed Ray cluster.

## 📋 Prerequisites

- Docker installed and running
- Docker Swarm initialized (will be done automatically)

## 🎯 One-Command Setup

For a complete rebuild and deploy:

```bash
./rebuild.sh
```

This single command will:
- Clean up old containers and stacks
- Build all images (head, worker, client)
- Deploy the cluster
- Monitor startup

## 🔨 Manual Build and Deploy

### 1. Build Images
```bash
./build-swarm.sh
```

This script will:
- Clean up old containers
- Build head, worker, and client images
- Use CPU-only dependencies (no CUDA)
- Avoid dependency conflicts

### 2. Deploy Cluster
```bash
./deploy-swarm.sh
```

This script will:
- Initialize Docker Swarm if needed
- Deploy the Ray cluster stack
- Monitor service startup
- Show cluster status

## 🎮 Run the Demo

Once the cluster is running, you can test it:

```bash
# Run the interactive demo
docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest
```

## 📊 Check Status

```bash
# Check service status
docker stack services ray-cluster

# View head node logs
docker service logs ray-cluster_ray-head

# View worker logs
docker service logs ray-cluster_ray-worker
```

## 🧹 Cleanup

To remove the cluster:

```bash
./cleanup.sh
```

## 🔧 Troubleshooting

### If services fail to start:
1. Check logs: `docker service logs ray-cluster_ray-head`
2. Use one-command rebuild: `./rebuild.sh`

### If workers don't register:
1. Check if old containers are running: `docker ps`
2. Use one-command rebuild: `./rebuild.sh`

## 📈 Scale Workers

To add more worker nodes:

```bash
docker service scale ray-cluster_ray-worker=5
```

## 🔗 Access Points

- **Ray Dashboard**: http://localhost:8265
- **Ray Port**: localhost:6379
- **Client Port**: localhost:10001

## 📁 File Structure

- `Dockerfile.head` - Self-contained head node image
- `Dockerfile.worker` - Self-contained worker node image  
- `Dockerfile.client` - Client image for running demos
- `build-swarm.sh` - Build all images
- `deploy-swarm.sh` - Deploy cluster
- `cleanup.sh` - Remove cluster
- `rebuild.sh` - Complete rebuild and deploy (recommended)
- `docker-swarm.yml` - Stack configuration 