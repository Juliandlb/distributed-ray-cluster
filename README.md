# Distributed Ray Cluster with Model Inference

This project demonstrates a distributed Ray cluster setup for running multiple lightweight language models in parallel. It uses Ray's distributed computing framework to manage model inference across multiple processes.

## Features

- Distributed Ray cluster setup for local development
- Multiple lightweight models running in parallel:
  - GPT-2 (tiny version)
  - DistilBERT
  - FLAN-T5 (small version)
- Memory usage tracking for each model
- Node information display (IP, hostname, Ray node ID)
- CPU-only inference support

## Project Structure

```
ray_cluster/
├── main.py           # Main script with model inference logic
├── cluster.yaml      # Ray cluster configuration
└── requirements.txt  # Project dependencies
```

## Prerequisites

- Python 3.13+
- Ray 2.9.0
- PyTorch 2.2.1
- Transformers 4.38.2

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Juliandlb/distributed-ray-cluster.git
cd distributed-ray-cluster
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r ray_cluster/requirements.txt
```

## Usage

1. Start the Ray head node:
```bash
ray start --head --port=6380 --redis-password='5241590000000000' --num-cpus=4
```

2. Start a worker node (in a new terminal):
```bash
ray start --address='192.168.0.16:6380' --redis-password='5241590000000000' --num-cpus=4
```

3. Run the main script:
```bash
python ray_cluster/main.py
```

## Current State

The project currently implements:
- A basic distributed Ray cluster setup
- Three different model types for inference:
  - Text generation (GPT-2)
  - Fill-mask completion (DistilBERT)
  - Text-to-text generation (T5)
- Memory usage tracking for each model
- Basic error handling and logging

## Memory Usage

The script tracks memory usage for each model:
- Initial memory usage
- Memory after model loading
- Memory during and after inference

## Node Information

Each model instance displays:
- IP Address
- Hostname
- Ray Node ID
- CUDA availability
- Memory statistics

## Future Improvements

Potential areas for enhancement:
1. Add GPU support
2. Implement model caching
3. Add more sophisticated error handling
4. Implement model-specific optimizations
5. Add monitoring and metrics collection
6. Support for more model types
7. Add API endpoints for inference

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 