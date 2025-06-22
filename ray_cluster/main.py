import ray
import time
import logging
import psutil
import socket
import torch
from typing import List, Dict, Any
import os
import sys
import argparse
import yaml
from datetime import datetime
from transformers import (
    AutoModelForCausalLM,
    AutoModelForMaskedLM,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    pipeline
)

# Add immediate debug output to confirm module loading
print("="*80)
print("[MODULE LOADING] main.py is being imported")
print("="*80)
print(f"[TIME] Import time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"[FILE] File: {__file__}")
print(f"[PYTHON] Python executable: {sys.executable}")

# Configure logging with a more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/app.log')
    ]
)

logger = logging.getLogger(__name__)
print("[OK] Logging configured")

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
    "distilgpt2": {
        "model_id": "distilgpt2",
        "max_length": 100,
        "temperature": 0.8,
        "model_class": AutoModelForCausalLM,
        "task": "text-generation",
        "pipeline_kwargs": {
            "max_length": 100,
            "temperature": 0.8,
            "do_sample": True,
            "pad_token_id": 50256
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

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_path}: {e}")
        return {}

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
        'shared': memory_info.shared / 1024 / 1024 if hasattr(memory_info, 'shared') else 0,  # MB
        'private': memory_info.private / 1024 / 1024 if hasattr(memory_info, 'private') else 0  # MB
    }

def log_memory_usage(node_id, model_name, pid, stage, initial_memory=None, final_memory=None):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    if initial_memory is None:
        memory = get_memory_usage()
        print(f"\n[{timestamp}] {model_name} (PID:{pid}) - {stage}")
        print(f"  RSS: {memory['rss']:.2f}MB")
        print(f"  VMS: {memory['vms']:.2f}MB")
        print(f"  Shared: {memory['shared']:.2f}MB")
        print(f"  Private: {memory['private']:.2f}MB")
    else:
        print(f"\n[{timestamp}] {model_name} (PID:{pid}) - {stage}")
        print(f"  RSS: {final_memory['rss']:.2f}MB (delta: {final_memory['rss'] - initial_memory['rss']:+.2f}MB)")
        print(f"  VMS: {final_memory['vms']:.2f}MB (delta: {final_memory['vms'] - initial_memory['vms']:+.2f}MB)")
        print(f"  Shared: {final_memory['shared']:.2f}MB (delta: {final_memory['shared'] - initial_memory['shared']:+.2f}MB)")
        print(f"  Private: {final_memory['private']:.2f}MB (delta: {final_memory['private'] - initial_memory['private']:+.2f}MB)")
    sys.stdout.flush()

@ray.remote
class LLMInferenceActor:
    def __init__(self, model_name: str, model_path: str = None):
        self.node_info = get_node_info()
        print(f"[ACTOR CREATION] {model_name} Model Instance")
        print(f"[NODE] Node: {self.node_info['hostname']} ({self.node_info['ip_address']})")
        self.model_name = model_name
        self.model_config = MODEL_CONFIGS[model_name]
        self.model_path = model_path or self.model_config['model_id']
        
        print(f"[MODEL] Model: {self.model_name}")
        print(f"[MODEL_ID] Model ID: {self.model_config['model_id']}")
        
        # Track memory before model loading
        initial_memory = self._get_memory_usage()
        print(f"[MEMORY] Initial memory usage:")
        print(f"  RSS: {initial_memory['rss']:.2f}MB")
        print(f"  VMS: {initial_memory['vms']:.2f}MB")
        print(f"  Shared: {initial_memory['shared']:.2f}MB")
        print(f"  Private: {initial_memory['private']:.2f}MB")
        
        # Load the model
        print(f"[LOADING] Loading model: {self.model_config['model_id']}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_config['model_id'])
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_config['model_id'],
            torch_dtype=torch.float16 if self.model_config.get('use_fp16', False) else torch.float32,
            device_map='auto' if self.model_config.get('use_device_map', False) else None
        )
        
        # Track memory after model loading
        final_memory = self._get_memory_usage()
        self._log_memory_change(initial_memory, final_memory, self.model_name, "MODEL_LOADED")
        
        print(f"\n[OK] [MODEL LOADED] {self.model_name} Ready for Inference")
    
    def _get_memory_usage(self):
        """Get current memory usage for this process"""
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'shared': memory_info.shared / 1024 / 1024 if hasattr(memory_info, 'shared') else 0,  # MB
            'private': memory_info.private / 1024 / 1024 if hasattr(memory_info, 'private') else 0  # MB
        }
    
    def _log_memory_change(self, initial_memory, final_memory, model_name, stage):
        """Log memory usage changes"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        if initial_memory:
            print(f"\n[{timestamp}] {model_name} (PID:{os.getpid()}) - {stage}")
            print(f"  RSS: {final_memory['rss']:.2f}MB (delta: {final_memory['rss'] - initial_memory['rss']:+.2f}MB)")
            print(f"  VMS: {final_memory['vms']:.2f}MB (delta: {final_memory['vms'] - initial_memory['vms']:+.2f}MB)")
            print(f"  Shared: {final_memory['shared']:.2f}MB (delta: {final_memory['shared'] - initial_memory['shared']:+.2f}MB)")
            print(f"  Private: {final_memory['private']:.2f}MB (delta: {final_memory['private'] - initial_memory['private']:+.2f}MB)")
        sys.stdout.flush()
    
    def generate(self, prompt: str) -> str:
        """Generate text based on the prompt"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        node_info = get_node_info()
        print(f"[PROMPT RECEIVED] {timestamp}")
        print(f"[NODE INFO] Hostname: {node_info['hostname']}, IP: {node_info['ip_address']}, Ray Node ID: {node_info['ray_node_id']}")
        print(f"[MODEL] {self.model_name}")
        print(f"[PROMPT] {prompt}")
        # Get memory usage before inference
        pre_inference_memory = self._get_memory_usage()
        # Generate response based on model type
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=inputs.input_ids.shape[1] + 50,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = generated_text[len(prompt):].strip()
        except Exception as e:
            print(f"[ERROR] Generation failed: {e}")
            response = f"Error generating response: {str(e)}"
        # Get memory usage after inference
        post_inference_memory = self._get_memory_usage()
        # Enhanced output logging
        print(f"[OK] [OPERATION COMPLETED] {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        print(f"[NODE INFO] Hostname: {node_info['hostname']}, IP: {node_info['ip_address']}, Ray Node ID: {node_info['ray_node_id']}")
        print(f"[MODEL] {self.model_name}")
        print(f"[RESPONSE] Generated {len(response)} characters")
        print(f"[RESPONSE TEXT] {response[:100]}{'...' if len(response) > 100 else ''}")
        sys.stdout.flush()
        return response

@ray.remote
class PromptCoordinator:
    def __init__(self, actors: List[ray.actor.ActorHandle]):
        self.actors = actors
        self.actors_dict = {f"actor_{i}": actor for i, actor in enumerate(actors)}
        
        print(f"[COORDINATOR] Prompt Coordinator initialized")
        print(f"[NODE] Node: {get_node_info()['hostname']} ({get_node_info()['ip_address']})")
        print(f"[MODELS] Available Models: {list(self.actors_dict.keys())}")
    
    def register_actor(self, actor: ray.actor.ActorHandle, model_name: str = None):
        """Register a new actor from a worker node"""
        actor_id = len(self.actors)
        self.actors.append(actor)
        actor_key = f"actor_{actor_id}"
        self.actors_dict[actor_key] = actor
        
        print(f"[COORDINATOR] Registered new actor: {actor_key}")
        print(f"[COORDINATOR] Total actors: {len(self.actors)}")
        print(f"[COORDINATOR] Available models: {list(self.actors_dict.keys())}")
        
        return actor_id
    
    def get_actor_count(self) -> int:
        """Get the number of available actors"""
        return len(self.actors)
    
    def get_actor_info(self) -> Dict[str, Any]:
        """Get information about available actors"""
        return {
            'total_actors': len(self.actors),
            'actor_keys': list(self.actors_dict.keys()),
            'node_info': get_node_info()
        }
    
    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process a prompt using all available actors"""
        request_timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"[COORDINATOR] Processing prompt: '{prompt[:50]}...'")
        print(f"[TIME] Timestamp: {request_timestamp}")
        print(f"[DISTRIBUTION] Distributing to {len(self.actors)} nodes...")
        
        if not self.actors:
            return {
                'prompt': prompt,
                'request_timestamp': request_timestamp,
                'total_actors': 0,
                'successful_responses': 0,
                'results': [],
                'consolidated_response': "No inference actors available. Please wait for worker nodes to join.",
                'error': 'NO_ACTORS_AVAILABLE'
            }
        
        # Submit tasks to all actors
        futures = []
        for i, actor in enumerate(self.actors):
            future = actor.generate.remote(prompt)
            futures.append(future)
        
        # Collect results
        results = []
        successful_responses = 0
        for i, future in enumerate(futures):
            try:
                result = ray.get(future)
                # Enhanced: get node info from actor (if possible)
                print(f"[OK] [NODE - {i}] Response received from actor {i}")
                print(f"[OK] [NODE - {i}] Response: {result[:100]}{'...' if len(result) > 100 else ''}")
                results.append({
                    'actor_id': i,
                    'response': result,
                    'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    'status': 'success'
                })
                successful_responses += 1
            except Exception as e:
                results.append({
                    'actor_id': i,
                    'response': f"Error: {str(e)}",
                    'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    'status': 'error'
                })
                print(f"[ERROR] [NODE - {i}] Failed: {e}")
        
        # Consolidate results
        consolidated_result = {
            'prompt': prompt,
            'request_timestamp': request_timestamp,
            'total_actors': len(self.actors),
            'successful_responses': successful_responses,
            'results': results,
            'consolidated_response': results[0]['response'] if results else "No responses received"
        }
        
        print(f"[OK] Successful Responses: {successful_responses}/{len(self.actors)}")
        
        # Log detailed results
        for result in results:
            if result['status'] == 'success':
                model_name = f"actor_{result['actor_id']}"
                print(f"\n[MODEL: {model_name.upper()}]")
                print(f"   [TIME] Time: {result['timestamp']}")
                print(f"   [RESPONSE] {result['response'][:100]}...")
            else:
                print(f"\n[ERROR] [MODEL: actor_{result['actor_id']}]")
                print(f"   [TIME] Time: {result['timestamp']}")
                print(f"   [ERROR] {result['response']}")
        
        print(f"\n[OK] [HEAD NODE - REQUEST COMPLETED] All responses logged and consolidated")
        
        return consolidated_result

def run_head_mode(config: Dict[str, Any]):
    """Run the application in head mode (coordinator only)."""
    print("\n" + "="*80)
    print("🎯 [HEAD NODE STARTING] Distributed Ray Cluster Coordinator")
    print("="*80)
    logger.info("Starting Ray cluster coordinator in head mode")
    
    # Initialize Ray in head mode
    ray.init(
        include_dashboard=True,
        dashboard_host='0.0.0.0',
        dashboard_port=8265,
        log_to_driver=True
    )
    
    print("\n✅ [CLUSTER STATUS] Ray Cluster Started Successfully")
    logger.info("Ray cluster initialized in head mode")
    
    # Head node no longer loads models - it's a pure coordinator
    print("\n🎯 [COORDINATOR MODE] Head Node is Coordinator Only")
    print("   📡 Waiting for worker nodes to join and register models...")
    print("   🤖 No models loaded on head node (memory optimized)")
    logger.info("Head node running in coordinator mode - no models loaded")
    
    # Create PromptCoordinator that will discover worker actors
    print(f"\n🎯 [REALTIME PROMPT SYSTEM] Initializing Prompt Coordinator...")
    
    # Create the prompt coordinator as a named actor in the default namespace
    # It will start with no actors and discover them as workers join
    prompt_coordinator = PromptCoordinator.options(name="prompt_coordinator").remote([])
    print(f"✅ Prompt Coordinator created and registered as 'prompt_coordinator'")
    print(f"📡 Coordinator will discover worker actors as they join")
    print(f"🎮 Use realtime_prompt_client.py to send prompts interactively")
    
    # Keep the cluster running for worker nodes to join
    print(f"\n" + "="*80)
    print("🔄 [CLUSTER RUNNING] Ready for Worker Nodes")
    print("="*80)
    print("Cluster coordinator is ready for worker nodes to join")
    print("Worker nodes will load models and register actors")
    print("Press Ctrl+C to stop the cluster")
    
    try:
        while True:
            time.sleep(10)
            # Print cluster status
            cluster_resources = ray.cluster_resources()
            print(f"\n📈 [CLUSTER STATUS] Resources: {cluster_resources}")
            
            # Try to get the coordinator to check available actors
            try:
                coordinator = ray.get_actor("prompt_coordinator")
                actor_count = ray.get(coordinator.get_actor_count.remote())
                print(f"🤖 [ACTOR STATUS] Available inference actors: {actor_count}")
            except Exception as e:
                print(f"🤖 [ACTOR STATUS] No actors available yet: {e}")
                
    except KeyboardInterrupt:
        print("\n🛑 [SHUTDOWN] Shutting down Ray cluster...")
        ray.shutdown()

def run_worker_mode(config: Dict[str, Any]):
    """Run the application in worker mode."""
    print("\n" + "="*80)
    print("🔧 [WORKER NODE STARTING] Joining Distributed Cluster")
    print("="*80)
    logger.info("Starting Ray worker node")
    
    # Ray is already initialized by the startup script, so we don't need to call ray.init()
    # The startup script handles connecting to the Ray cluster
    
    print("\n✅ [CLUSTER CONNECTION] Worker Node Successfully Joined Cluster")
    logger.info("Worker node successfully joined the cluster")
    
    # Get node information for display
    node_info = get_node_info()
    print(f"   📍 Node: {node_info['hostname']} ({node_info['ip_address']})")
    print(f"   🆔 Ray Node ID: {node_info['ray_node_id']}")
    print(f"   🖥️  CUDA Available: {node_info['cuda_available']}")
    
    # Create inference actors for this worker
    print(f"\n🤖 [MODEL DEPLOYMENT] Creating Model Instances on Worker Node")
    logger.info("Creating model instances on worker node...")
    
    model_names = config.get('models', {}).get('preload', ["tiny-gpt2", "distilbert", "flan-t5-small"])
    actors = []
    
    for model_name in model_names:
        if model_name in MODEL_CONFIGS:
            actor = LLMInferenceActor.remote(model_name)
            actors.append(actor)
            print(f"   ✅ Created actor for model: {model_name}")
            logger.info(f"Created actor for model: {model_name}")
        else:
            print(f"   ⚠️  Unknown model: {model_name}")
            logger.warning(f"Unknown model: {model_name}")
    
    if not actors:
        print("   ❌ No valid models to load")
        logger.error("No valid models to load")
        return
    
    print(f"   📊 Total actors created on worker: {len(actors)}")
    
    # Register actors with the coordinator
    print(f"\n📡 [ACTOR REGISTRATION] Registering Actors with Coordinator")
    try:
        coordinator = ray.get_actor("prompt_coordinator")
        print(f"   ✅ Found coordinator, registering {len(actors)} actors...")
        
        for i, actor in enumerate(actors):
            actor_id = ray.get(coordinator.register_actor.remote(actor, model_names[i]))
            print(f"   ✅ Registered actor {i+1}/{len(actors)} with ID: {actor_id}")
        
        print(f"   🎯 All actors registered successfully!")
        
        # Get coordinator status
        actor_info = ray.get(coordinator.get_actor_info.remote())
        print(f"   📊 Coordinator reports {actor_info['total_actors']} total actors available")
        
    except Exception as e:
        print(f"   ❌ Failed to register actors with coordinator: {e}")
        print(f"   ⚠️  Actors will work locally but not be coordinated")
        logger.error(f"Failed to register actors with coordinator: {e}")
    
    print(f"\n" + "="*80)
    print("🟢 [WORKER NODE READY] Active and Waiting for Tasks")
    print("="*80)
    print(f"✅ Loaded {len(actors)} models and ready for inference")
    print(f"🔄 Worker node will remain active for incoming requests")
    print(f"📊 Models available: {', '.join(model_names)}")
    print(f"📍 Node: {node_info['hostname']} ({node_info['ip_address']})")
    
    # Keep the worker running
    try:
        while True:
            time.sleep(30)
            # Print worker status
            current_node_info = get_node_info()
            print(f"\n📈 [WORKER STATUS] Node: {current_node_info['hostname']}")
            print(f"   🆔 Ray ID: {current_node_info['ray_node_id']}")
            print(f"   📍 IP: {current_node_info['ip_address']}")
            print(f"   🤖 Active Models: {len(actors)}")
            print(f"   ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    except KeyboardInterrupt:
        print("\n🛑 [SHUTDOWN] Shutting down worker node...")
        ray.shutdown()

def main():
    # Add immediate debug logging to confirm execution
    print("="*80)
    print("[MAIN.PY STARTING] Application initialization")
    print("="*80)
    print(f"[TIME] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[PYTHON] Python version: {sys.version}")
    print(f"[DIR] Working directory: {os.getcwd()}")
    print(f"[USER] User: {os.getenv('USER', 'unknown')}")
    print(f"[HOST] Hostname: {socket.gethostname()}")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Ray Cluster LLM Inference')
    parser.add_argument('--mode', choices=['head', 'worker'], default='head',
                       help='Run mode: head (cluster leader) or worker (cluster member)')
    parser.add_argument('--config', type=str, default=None,
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    print(f"🎯 Mode: {args.mode}")
    print(f"⚙️  Config file: {args.config}")
    
    # Set environment variables to disable log deduplication and reduce Ray logging
    os.environ["RAY_DEDUP_LOGS"] = "0"
    os.environ["RAY_DISABLE_DEDUP"] = "1"
    os.environ["RAY_DISABLE_CUSTOM_LOGGER"] = "1"
    
    print("✅ Environment variables set")
    
    # Load configuration
    config = {}
    if args.config:
        try:
            config = load_config(args.config)
            print(f"✅ Configuration loaded from {args.config}")
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            config = {}
    else:
        print("ℹ️  No config file specified, using defaults")
    
    print("🔄 Starting Ray cluster...")
    
    # Run in appropriate mode
    if args.mode == 'head':
        print("[HEAD] Starting Ray head node...")
        # Start Ray head node
        ray.init(
            include_dashboard=True,
            dashboard_host='0.0.0.0',
            dashboard_port=8265,
            log_to_driver=True
        )
        print("[HEAD] Ray head node started successfully")
        
        # Create actors for each model
        print("[HEAD] Creating model actors...")
        actors = []
        for model_name in MODEL_CONFIGS.keys():
            print(f"[HEAD] Creating actor for {model_name}...")
            actor = LLMInferenceActor.remote(model_name)
            actors.append(actor)
            print(f"[HEAD] Actor for {model_name} created successfully")
        
        # Create prompt coordinator
        print("[HEAD] Creating prompt coordinator...")
        coordinator = PromptCoordinator.remote(actors)
        print("[HEAD] Prompt coordinator created successfully")
        
        # Process some example prompts
        print("[HEAD] Processing example prompts...")
        example_prompts = [
            "The quick brown fox",
            "In a world where",
            "The future of AI",
            "Machine learning is",
            "Distributed computing"
        ]
        
        for i, prompt in enumerate(example_prompts):
            print(f"[HEAD] Processing prompt {i+1}: '{prompt[:30]}...'")
            result = ray.get(coordinator.process_prompt.remote(prompt))
            if isinstance(result, dict) and 'consolidated_response' in result:
                response = result['consolidated_response']
                print(f"[HEAD] Result {i+1}: {response[:100]}...")
            else:
                print(f"[HEAD] Result {i+1}: {str(result)[:100]}...")
        
        print("[HEAD] Example processing completed")
        
        # Keep the head node running
        print("[HEAD] Head node is running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[HEAD] Shutting down head node...")
            ray.shutdown()
    
    elif args.mode == 'worker':
        print("[WORKER] Starting Ray worker node...")
        # Connect to existing Ray cluster
        ray.init(address='ray-head:6379')
        print("[WORKER] Connected to Ray cluster successfully")
        
        # Create actors for each model
        print("[WORKER] Creating model actors...")
        actors = []
        for model_name in MODEL_CONFIGS.keys():
            print(f"[WORKER] Creating actor for {model_name}...")
            actor = LLMInferenceActor.remote(model_name)
            actors.append(actor)
            print(f"[WORKER] Actor for {model_name} created successfully")
        
        # Create prompt coordinator
        print("[WORKER] Creating prompt coordinator...")
        coordinator = PromptCoordinator.remote(actors)
        print("[WORKER] Prompt coordinator created successfully")
        
        # Process some example prompts
        print("[WORKER] Processing example prompts...")
        example_prompts = [
            "The quick brown fox",
            "In a world where",
            "The future of AI",
            "Machine learning is",
            "Distributed computing"
        ]
        
        for i, prompt in enumerate(example_prompts):
            print(f"[WORKER] Processing prompt {i+1}: '{prompt[:30]}...'")
            result = ray.get(coordinator.process_prompt.remote(prompt))
            if isinstance(result, dict) and 'consolidated_response' in result:
                response = result['consolidated_response']
                print(f"[WORKER] Result {i+1}: {response[:100]}...")
            else:
                print(f"[WORKER] Result {i+1}: {str(result)[:100]}...")
        
        print("[WORKER] Example processing completed")
        
        # Keep the worker node running
        print("[WORKER] Worker node is running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[WORKER] Shutting down worker node...")
            ray.shutdown()
    else:
        logger.error(f"Unknown mode: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
