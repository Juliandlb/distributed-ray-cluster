# Distributed Ray Cluster with Model Inference

This repository implements a **distributed inference system inspired by Ray on Golem**, demonstrating how to build scalable, distributed language model inference using Ray's distributed computing framework. The project serves as a proof-of-concept for running multiple lightweight language models in parallel across a distributed cluster.

## 🎯 **Project Goal**

This project aims to explore and implement distributed inference capabilities similar to those found in Ray on Golem, but focused on local and containerized deployments. It demonstrates how to:

- Distribute model inference across multiple nodes
- Scale horizontally by adding worker nodes dynamically
- Balance load across the cluster automatically
- Monitor and manage distributed resources efficiently

## 📚 **Development Documentation**

**All detailed development work, implementation details, and technical documentation for this project is maintained in the `ray_cluster/README.md` file.** This includes:

- Complete setup and deployment instructions
- Architecture details and configuration options
- Testing results and performance metrics
- Troubleshooting guides and best practices
- Latest improvements and feature updates

**For the most up-to-date and comprehensive information, please refer to:**
```
ray_cluster/README.md
```

## Features

- Distributed Ray cluster setup for local development
- Multiple lightweight models running in parallel:
  - GPT-2 (tiny version)
  - DistilBERT
  - FLAN-T5 (small version)
- Memory usage tracking for each model
- Node information display (IP, hostname, Ray node ID)
- CPU-only inference support
- Containerized deployment with Docker
- Dynamic worker node scaling

## Project Structure

```
distributed-ray-cluster/
├── ray_cluster/           # Main implementation directory
│   ├── README.md         # Complete development documentation
│   ├── main.py           # Main script with model inference logic
│   ├── docker-compose.yml # Container orchestration
│   ├── Dockerfile.*      # Container definitions
│   └── requirements.txt  # Project dependencies
├── ray_on_golem/         # Golem-specific implementations (future)
└── README.md             # This overview file
```

## Quick Start

For detailed setup and usage instructions, see `ray_cluster/README.md`. Here's a brief overview:

1. **Clone the repository:**
```bash
git clone https://github.com/Juliandlb/distributed-ray-cluster.git
cd distributed-ray-cluster
```

2. **Start the cluster (laptop mode):**
```bash
cd ray_cluster
docker-compose -f docker-compose.laptop.yml up -d ray-head
```

3. **Add worker nodes:**
```bash
./add_workers.sh 2  # Add 2 worker nodes
```

4. **Run distributed inference:**
```bash
python test_distributed_inference.py
```

## Current State

The project successfully implements:
- ✅ **Containerized distributed Ray cluster** with head and worker nodes
- ✅ **Dynamic scaling** - worker nodes can join/leave at runtime
- ✅ **Load balancing** - automatic distribution of inference tasks
- ✅ **Multiple model types** - GPT-2, DistilBERT, and T5 models
- ✅ **Memory monitoring** - tracking resource usage across nodes
- ✅ **Health checks** - reliable cluster monitoring
- ✅ **Laptop optimization** - configurations for limited resources

## Future Roadmap

This project serves as a foundation for exploring distributed inference concepts that could be applied to:

1. **Ray on Golem Integration** - Extending to Golem network for decentralized computing
2. **Cloud Deployment** - Scaling to cloud providers
3. **Advanced Load Balancing** - Implementing more sophisticated distribution algorithms
4. **Model Optimization** - Adding quantization and optimization techniques
5. **API Development** - Building REST APIs for inference requests

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For detailed development guidelines, see `ray_cluster/README.md`. 