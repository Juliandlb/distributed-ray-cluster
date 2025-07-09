# 💻 Remote Worker Node Instructions

**Your VM is ready!** Now set up your remote worker node to join the Ray cluster.

## 🚀 Quick Setup (5 minutes)

### **Step 1: Install Docker (if not installed)**
```bash
# For Arch Linux:
sudo pacman -S docker

# For Ubuntu/Debian:
sudo apt update && sudo apt install docker.io

# For CentOS/RHEL:
sudo yum install docker

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in, or run: newgrp docker
```

### **Step 2: Clone the Repository**
```bash
git clone https://github.com/Juliandlb/distributed-ray-cluster.git
cd distributed-ray-cluster/ray_cluster
```

### **Step 3: Test Connection to VM**
```bash
# Test if you can reach the VM
ping 10.11.0.4

# Test Ray port (should connect)
telnet 10.11.0.4 6379

# Test dashboard (should show Ray UI)
curl http://10.11.0.4:8265
```

### **Step 4: Join as Remote Worker**
```bash
# Make script executable
chmod +x start_standalone_worker.sh

# Join the cluster
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

## 🎮 Test the Multi-Machine Cluster

### **Option 1: Test from VM (Recommended)**
On your VM, run:
```bash
docker run --rm -it --network ray-cluster_ray-cluster ray-cluster-client:latest
```

### **Option 2: Test from Remote Worker Node**
```bash
# Build client image on your remote worker
docker build -f Dockerfile.client -t ray-cluster-client:latest .

# Run the test
docker run --rm -it ray-cluster-client:latest
```

## 📊 Monitor the Cluster

- **Ray Dashboard**: http://10.11.0.4:8265
- **Check Worker**: `docker logs ray-standalone-worker`
- **Check Status**: `docker ps | grep ray-standalone-worker`

## 🧹 Cleanup

When done testing:
```bash
# Stop the worker
docker stop ray-standalone-worker
docker rm ray-standalone-worker
```

## 🔧 Troubleshooting

### **If you can't connect to VM:**
```bash
# Check if ports are open on VM
telnet 10.11.0.4 6379

# If it fails, the VM might need firewall rules
# Contact the VM admin to open ports 6379, 8265, 12345-12346
```

### **If Docker doesn't work:**
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker
```

## 🎯 Success Criteria

✅ You should see:
1. Worker container running on your remote worker node
2. Worker appears in Ray dashboard at http://10.11.0.4:8265
3. Interactive prompts are processed on your remote worker node
4. Response shows your remote worker's hostname/IP

**That's it! Your remote worker node is now part of the VM's Ray cluster! 🎉** 