import ray
import time
import logging
import psutil
import socket
import torch
from typing import List, Dict, Any
import os
import sys
from datetime import datetime
from transformers import (
    AutoModelForCausalLM,
    AutoModelForMaskedLM,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    pipeline
)

# Configure logging with a more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

logger = logging.getLogger(__name__)

# Model configurations
MODEL_CONFIGS = {
    "tiny-gpt2": {
        "model_id": "sshleifer/tiny-gpt2",
        "max_length": 50,
        "temperature": 0.7,
        "model_class": AutoModelForCausalLM,
        "task": "text-generation",
        "pipeline_kwargs": {
            "max_length": 50,
            "temperature": 0.7
        }
    },
    "distilbert": {
        "model_id": "distilbert-base-uncased",
        "max_length": 50,
        "temperature": 0.7,
        "model_class": AutoModelForMaskedLM,
        "task": "fill-mask",
        "pipeline_kwargs": {}  # No special parameters needed for fill-mask
    },
    "flan-t5-small": {
        "model_id": "google/flan-t5-small",
        "max_length": 50,
        "temperature": 0.7,
        "model_class": AutoModelForSeq2SeqLM,
        "task": "text2text-generation",
        "pipeline_kwargs": {
            "max_length": 50,
            "temperature": 0.7
        }
    }
}

def get_node_info() -> Dict[str, Any]:
    """Get information about the current node."""
    return {
        'ip_address': socket.gethostbyname(socket.gethostname()),
        'hostname': socket.gethostname(),
        'ray_node_id': ray.get_runtime_context().get_node_id(),
        'cuda_available': torch.cuda.is_available() if torch is not None else False,
        'cuda_device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
    }

def get_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    return {
        'rss': memory_info.rss / 1024 / 1024,  # MB
        'vms': memory_info.vms / 1024 / 1024,  # MB
        'shared': memory_info.shared / 1024 / 1024 if hasattr(memory_info, 'shared') else 0  # MB
    }

def log_memory_usage(node_id, model_name, pid, stage, initial_memory=None, final_memory=None):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    if initial_memory is None:
        memory = get_memory_usage()
        print(f"\n[{timestamp}] {model_name} (PID:{pid}) - {stage}")
        print(f"  RSS: {memory['rss']:.2f}MB")
        print(f"  VMS: {memory['vms']:.2f}MB")
        print(f"  Shared: {memory['shared']:.2f}MB")
    else:
        print(f"\n[{timestamp}] {model_name} (PID:{pid}) - {stage}")
        print(f"  RSS: {final_memory['rss']:.2f}MB (Δ: {final_memory['rss'] - initial_memory['rss']:+.2f}MB)")
        print(f"  VMS: {final_memory['vms']:.2f}MB (Δ: {final_memory['vms'] - initial_memory['vms']:+.2f}MB)")
        print(f"  Shared: {final_memory['shared']:.2f}MB (Δ: {final_memory['shared'] - initial_memory['shared']:+.2f}MB)")
    sys.stdout.flush()

@ray.remote
class LLMInferenceActor:
    def __init__(self, model_name: str = "tiny-gpt2"):
        self.model_name = model_name
        self.model_config = MODEL_CONFIGS[model_name]
        self.node_info = get_node_info()
        self.pid = os.getpid()
        
        # Print node information
        print(f"\n=== Node Information ===")
        print(f"IP Address: {self.node_info['ip_address']}")
        print(f"Hostname: {self.node_info['hostname']}")
        print(f"Ray Node ID: {self.node_info['ray_node_id']}")
        print(f"CUDA Available: {self.node_info['cuda_available']}")
        if self.node_info['cuda_available']:
            print(f"CUDA Device Count: {self.node_info['cuda_device_count']}")
        
        # Get initial memory usage
        initial_memory = get_memory_usage()
        log_memory_usage(self.node_info['ray_node_id'], self.model_name, self.pid, "Initial memory usage")
        
        # Load model and tokenizer
        print(f"\nLoading model: {self.model_config['model_id']}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_config['model_id'])
        self.model = self.model_config['model_class'].from_pretrained(self.model_config['model_id'])
        
        # Create pipeline for easier inference
        self.pipe = pipeline(
            self.model_config['task'],
            model=self.model,
            tokenizer=self.tokenizer,
            **self.model_config['pipeline_kwargs']
        )
        
        # Get final memory usage after loading
        final_memory = get_memory_usage()
        log_memory_usage(self.node_info['ray_node_id'], self.model_name, self.pid, "After loading", initial_memory, final_memory)
    
    def generate(self, prompt: str) -> str:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n[{timestamp}] {self.model_name} (PID:{self.pid}) - Processing: {prompt[:30]}...")
        sys.stdout.flush()
        
        # Get memory usage before inference
        pre_inference_memory = get_memory_usage()
        
        # Generate response based on model type
        if self.model_name == "distilbert":
            # For DistilBERT, we'll use a simple fill-mask example
            response = self.pipe(f"{prompt} [MASK]")[0]['sequence']
        else:
            # For GPT-2 and T5, we can use text generation
            response = self.pipe(prompt)[0]['generated_text']
        
        # Get memory usage after inference
        post_inference_memory = get_memory_usage()
        log_memory_usage(self.node_info['ray_node_id'], self.model_name, self.pid, "After inference", pre_inference_memory, post_inference_memory)
        
        return response

def main():
    # Set environment variables to disable log deduplication and reduce Ray logging
    os.environ["RAY_DEDUP_LOGS"] = "0"
    os.environ["RAY_DISABLE_DEDUP"] = "1"
    os.environ["RAY_DISABLE_CUSTOM_LOGGER"] = "1"
    
    # Initialize Ray if not already running
    if not ray.is_initialized():
        ray.init(
            logging_level=logging.INFO,
            log_to_driver=True,
            include_dashboard=False
        )
    
    print("\n=== Starting Ray Cluster ===")
    logger.info("Ray cluster initialized")
    
    # Create inference actors with different model sizes
    print("\n=== Creating Model Instances ===")
    logger.info("Creating model instances...")
    actors = [
        LLMInferenceActor.remote("tiny-gpt2"),
        LLMInferenceActor.remote("distilbert"),
        LLMInferenceActor.remote("flan-t5-small")
    ]
    
    # Example prompts
    prompts = [
        "What is machine learning?",
        "Explain quantum computing",
        "Tell me about Ray",
        "What is distributed computing?",
        "Explain LLM inference"
    ]
    
    # Dispatch inference calls concurrently
    print("\n=== Starting Concurrent Inference ===")
    logger.info("Starting concurrent inference...")
    futures = []
    for i, prompt in enumerate(prompts):
        # Round-robin assignment to actors
        actor = actors[i % len(actors)]
        futures.append(actor.generate.remote(prompt))
    
    # Get results
    results = ray.get(futures)
    
    # Print results
    print("\n=== Inference Results ===")
    for prompt, result in zip(prompts, results):
        print(f"\nPrompt: {prompt}")
        print(f"Response: {result}")

if __name__ == "__main__":
    main()
