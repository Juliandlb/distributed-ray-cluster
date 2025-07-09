# 🚀 Multi-Machine Ray Cluster Demo (Docker Swarm)

This guide shows how to run a Ray cluster across multiple machines using Docker Swarm for internet-ready, secure, and scalable deployment.

## 🎯 Overview

- **Manager Node (Head)**: Runs the Ray cluster coordinator and manages the Swarm
- **Worker Nodes**: Join the Swarm and run Ray workers
- **All nodes**: Use Docker Swarm overlay network for secure communication

## 🖥️ Manager Node: Start the Cluster

```bash
# On the manager (head) node
cd /path/to/ray_cluster
chmod +x start_cluster.sh
./start_cluster.sh
```

**Expected Output:**
```
🚀 Starting Ray Cluster (Head Node)
==================================
📍 Public IP: <manager-public-ip>
🔑 Join Token: <token>
...
```

## 🤖 Worker Node: Join the Swarm

```bash
# On each remote worker node
# Use the join token and public IP from the manager's output
sudo docker swarm join --token <token> <manager-public-ip>:2377
```

**Verify on manager:**
```bash
docker node ls
```

## 🛠️ Deploy/Scale Ray Workers (from Manager)

```bash
# Deploy the stack (if not already running)
./rebuild.sh

# Scale up workers (from manager)
docker service scale ray-cluster_ray-worker=3
```

## 🎮 Test the Multi-Machine Cluster

```bash
# On the manager node
docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest
```

## 📊 Monitor the Cluster

- **Ray Dashboard**: http://<manager-public-ip>:8265
- **Check Swarm nodes**: `docker node ls`
- **Check Ray services**: `docker stack services ray-cluster`
- **Check logs**: `docker service logs ray-cluster_ray-worker`

## 🔧 Troubleshooting

- **Open required ports on all nodes:**
  - 2377/tcp (Swarm management)
  - 7946/tcp, 7946/udp (Swarm communication)
  - 4789/udp (Overlay network)
  - 6379/tcp (Ray)
  - 8265/tcp (Dashboard)
- **If a worker can't join:**
  - Check firewall and network connectivity
  - Ensure Docker is running and up to date
  - Use the correct join token and public IP

## 🧹 Cleanup

```bash
# Remove the stack (from manager)
./cleanup.sh

# Remove a worker node (from worker)
docker swarm leave
```

## 🚀 Next Steps

- Add more workers: Join more nodes and scale the service
- Use placement constraints for advanced scheduling
- Monitor with Ray dashboard and Docker Swarm tools

The demo is now ready for secure, scalable, internet-based deployment! 🎉 