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
    "gpt2": {
        "model_id": "gpt2",
        "max_length": 100,
        "temperature": 0.8,
        "model_class": AutoModelForCausalLM,
        "task": "text-generation",
        "pipeline_kwargs": {
            "max_length": 100,
            "temperature": 0.8,
            "do_sample": True,
            "pad_token_id": 50256,
            "top_k": 50,
            "top_p": 0.9
        }
    },
    "gpt2-medium": {
        "model_id": "gpt2-medium",
        "max_length": 150,
        "temperature": 0.8,
        "model_class": AutoModelForCausalLM,
        "task": "text-generation",
        "pipeline_kwargs": {
            "max_length": 150,
            "temperature": 0.8,
            "do_sample": True,
            "pad_token_id": 50256,
            "top_k": 50,
            "top_p": 0.9
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
            "pad_token_id": 50256,
            "top_k": 50,
            "top_p": 0.9
        }
    },
    "microsoft/DialoGPT-medium": {
        "model_id": "microsoft/DialoGPT-medium",
        "max_length": 100,
        "temperature": 0.8,
        "model_class": AutoModelForCausalLM,
        "task": "text-generation",
        "pipeline_kwargs": {
            "max_length": 100,
            "temperature": 0.8,
            "do_sample": True,
            "pad_token_id": 50256,
            "top_k": 50,
            "top_p": 0.9
        }
    },
    "google/flan-t5-small": {
        "model_id": "google/flan-t5-small",
        "max_length": 100,
        "temperature": 0.7,
        "model_class": AutoModelForSeq2SeqLM,
        "task": "text2text-generation",
        "pipeline_kwargs": {
            "max_length": 100,
            "temperature": 0.7,
            "do_sample": True
        }
    },
    "google/flan-t5-base": {
        "model_id": "google/flan-t5-base",
        "max_length": 150,
        "temperature": 0.7,
        "model_class": AutoModelForSeq2SeqLM,
        "task": "text2text-generation",
        "pipeline_kwargs": {
            "max_length": 150,
            "temperature": 0.7,
            "do_sample": True
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

def get_node_label(node_info: Dict[str, Any], is_head: bool = False, worker_number: int = None) -> str:
    """Get a human-readable label for a node."""
    if is_head:
        return "Head Node"
    elif worker_number is not None:
        return f"Worker Node #{worker_number}"
    else:
        # Try to determine if it's a worker by hostname pattern
        hostname = node_info.get('hostname', '')
        if 'worker' in hostname.lower():
            # Extract number from hostname if possible
            import re
            numbers = re.findall(r'\d+', hostname)
            if numbers:
                return f"Worker Node #{numbers[0]}"
            else:
                return "Worker Node"
        else:
            return "Unknown Node"

def get_cluster_node_mapping() -> Dict[str, Dict[str, Any]]:
    """Get a mapping of all nodes in the cluster with proper labels."""
    try:
        nodes = ray.nodes()
        node_mapping = {}
        worker_count = 0
        
        for node in nodes:
            node_id = node['NodeID']
            hostname = node.get('Hostname', 'unknown')
            ip = node.get('NodeIP', 'unknown')
            alive = node.get('Alive', False)
            resources = node.get('Resources', {})
            
            # Determine if this is the head node
            is_head = node_id == ray.get_runtime_context().get_node_id() or 'head' in hostname.lower()
            
            if is_head:
                label = "Head Node"
                node_type = "head"
            else:
                worker_count += 1
                label = f"Worker Node #{worker_count}"
                node_type = "worker"
            
            node_mapping[node_id] = {
                'hostname': hostname,
                'ip': ip,
                'alive': alive,
                'resources': resources,
                'label': label,
                'type': node_type,
                'worker_number': worker_count if not is_head else None,
                'actor_count': 0  # Will be updated later
            }
        
        return node_mapping
    except Exception as e:
        print(f"[WARNING] Could not get cluster node mapping: {e}")
        return {}

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
        self.model_name = model_name
        self.model_config = MODEL_CONFIGS.get(model_name, {})
        
        # Get node information for this actor
        self.node_info = get_node_info()
        
        # Determine if this is running on head or worker
        # Check container name to determine node type
        hostname = self.node_info['hostname']
        
        # Check if this is the head node by looking for 'head' in hostname
        # or by checking if it's the current node (head node runs the coordinator)
        is_head = 'head' in hostname.lower()
        
        if is_head:
            self.node_label = "Head Node"
        else:
            # This is a worker node
            # Since hostname is a random container ID, we'll use a simple approach
            # In a real deployment, you'd use environment variables or container names
            
            # For now, assume it's the first worker
            # In a multi-worker setup, you'd use environment variables like WORKER_NUMBER
            worker_number = 1
            
            # Try to get worker number from environment variable if available
            import os
            env_worker_number = os.environ.get('WORKER_NUMBER')
            if env_worker_number:
                try:
                    worker_number = int(env_worker_number)
                except ValueError:
                    worker_number = 1
            
            self.node_label = f"Worker Node #{worker_number}"
        
        print(f"[ACTOR CREATION] {model_name} Model Instance")
        print(f"[NODE] {self.node_label}: {self.node_info['hostname']} ({self.node_info['ip_address']})")
        print(f"[MODEL] Model: {model_name}")
        print(f"[MODEL_ID] Model ID: {self.model_config['model_id']}")
        
        # Track memory before model loading
        initial_memory = self._get_memory_usage()
        
        # Load the model
        print(f"[LOADING] Loading model: {self.model_config['model_id']}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_config['model_id'])
        self.model = AutoModelForCausalLM.from_pretrained(self.model_config['model_id'])
        
        # Track memory after model loading
        final_memory = self._get_memory_usage()
        self._log_memory_change(initial_memory, final_memory, self.model_name, "MODEL_LOADED")
        
        print(f"\n[OK] [MODEL LOADED] {self.model_name} Ready for Inference")
        print(f"[NODE] Running on: {self.node_label} ({self.node_info['hostname']})")

    def _get_memory_usage(self):
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except:
            return 0

    def _log_memory_change(self, initial_memory, final_memory, model_name, stage):
        """Log memory usage change"""
        if initial_memory and final_memory:
            change_mb = (final_memory - initial_memory) / 1024 / 1024
            print(f"[MEMORY] {stage}: {change_mb:.1f}MB change for {model_name}")

    def get_node_info(self) -> Dict[str, Any]:
        """Get current node information for this actor"""
        node_info = get_node_info()
        node_info['node_label'] = self.node_label
        return node_info

    def generate(self, prompt: str) -> str:
        """Generate response for the given prompt"""
        start_time = time.time()
        
        # Get current node info for this request
        current_node_info = get_node_info()
        current_node_info['node_label'] = self.node_label
        
        print(f"\n[INFERENCE] Processing prompt on {self.node_label}")
        print(f"[NODE] {self.node_label}: {current_node_info['hostname']} ({current_node_info['ip_address']})")
        print(f"[MODEL] Model: {self.model_name}")
        print(f"[PROMPT] '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
        
        try:
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 50,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the original prompt from response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"[RESPONSE] Generated in {processing_time:.2f}s")
            print(f"[NODE] Response from: {self.node_label} ({current_node_info['ip_address']})")
            
            # Return response with node information
            return {
                'response': response,
                'node_hostname': current_node_info['hostname'],
                'node_ip': current_node_info['ip_address'],
                'node_id': current_node_info['ray_node_id'],
                'node_label': self.node_label,
                'model_name': self.model_name,
                'processing_time': processing_time
            }
            
        except Exception as e:
            print(f"[ERROR] Generation failed: {e}")
            return {
                'response': f"Error generating response: {str(e)}",
                'node_hostname': current_node_info['hostname'],
                'node_ip': current_node_info['ip_address'],
                'node_id': current_node_info['ray_node_id'],
                'node_label': self.node_label,
                'model_name': self.model_name,
                'processing_time': time.time() - start_time,
                'error': str(e)
            }

@ray.remote
class PromptCoordinator:
    def __init__(self, actors: List[ray.actor.ActorHandle]):
        self.actors = actors
        self.actor_info = {}  # Track actor details including node info
        print(f"[COORDINATOR] Prompt Coordinator initialized")
        print(f"[COORDINATOR] Available models: {[f'actor_{i}' for i in range(len(actors))]}")

    def register_actor(self, actor: ray.actor.ActorHandle, model_name: str = None):
        """Register a new actor with the coordinator"""
        print(f"[COORDINATOR DEBUG] register_actor called with model_name: {model_name}")
        print(f"[COORDINATOR DEBUG] Actor handle type: {type(actor)}")
        print(f"[COORDINATOR DEBUG] Current actors count: {len(self.actors)}")
        
        actor_id = len(self.actors)
        self.actors.append(actor)
        
        print(f"[COORDINATOR DEBUG] Actor added to list, new count: {len(self.actors)}")
        
        # Get node info for this actor
        try:
            print(f"[COORDINATOR DEBUG] Attempting to get node info for actor {actor_id}...")
            node_info = ray.get(actor.get_node_info.remote())
            print(f"[COORDINATOR DEBUG] Node info received: {node_info}")
            
            self.actor_info[actor_id] = {
                'model_name': model_name,
                'node_hostname': node_info['hostname'],
                'node_ip': node_info['ip_address'],
                'node_id': node_info['ray_node_id'],
                'node_label': node_info.get('node_label', 'Unknown Node')
            }
            print(f"[COORDINATOR DEBUG] Actor info stored: {self.actor_info[actor_id]}")
        except Exception as e:
            print(f"[COORDINATOR DEBUG] Failed to get node info: {e}")
            # Fallback if node info not available
            self.actor_info[actor_id] = {
                'model_name': model_name,
                'node_hostname': 'unknown',
                'node_ip': 'unknown',
                'node_id': 'unknown',
                'node_label': 'Unknown Node'
            }
        
        print(f"[COORDINATOR] Registered actor {actor_id} ({model_name}) on {self.actor_info[actor_id]['node_label']}")
        print(f"[COORDINATOR DEBUG] Total actors now: {len(self.actors)}")
        print(f"[COORDINATOR DEBUG] Actor info keys: {list(self.actor_info.keys())}")
        return actor_id

    def get_actor_count(self) -> int:
        """Get the number of available actors"""
        return len(self.actors)

    def get_actor_info(self) -> Dict[str, Any]:
        """Get detailed information about all actors"""
        return {
            'total_actors': len(self.actors),
            'actors': self.actor_info,
            'cluster_nodes': self._get_cluster_nodes()
        }
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status including node information"""
        cluster_resources = ray.cluster_resources()
        cluster_nodes = self._get_cluster_nodes()
        
        return {
            'total_actors': len(self.actors),
            'cluster_resources': cluster_resources,
            'cluster_nodes': cluster_nodes,
            'actor_details': self.actor_info
        }
    
    def _get_cluster_nodes(self) -> Dict[str, Any]:
        """Get information about all nodes in the cluster"""
        try:
            # Get all nodes in the cluster with proper labels
            node_mapping = get_cluster_node_mapping()
            
            # Count actors per node
            for actor_id, info in self.actor_info.items():
                node_id = info['node_id']
                if node_id in node_mapping:
                    node_mapping[node_id]['actor_count'] = node_mapping[node_id].get('actor_count', 0) + 1
            
            return node_mapping
        except Exception as e:
            print(f"[WARNING] Could not get cluster nodes: {e}")
            return {}

    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process a prompt using all available actors"""
        request_timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        
        # Get cluster status
        cluster_status = self.get_cluster_status()
        
        print(f"[COORDINATOR] Processing prompt: '{prompt[:50]}...'")
        print(f"[TIME] Timestamp: {request_timestamp}")
        print(f"[CLUSTER] Total nodes: {len(cluster_status['cluster_nodes'])}")
        print(f"[CLUSTER] Total actors: {len(self.actors)}")
        print(f"[DISTRIBUTION] Distributing to {len(self.actors)} actors...")
        
        if not self.actors:
            return {
                'prompt': prompt,
                'request_timestamp': request_timestamp,
                'total_actors': 0,
                'successful_responses': 0,
                'results': [],
                'consolidated_response': "No inference actors available. Please wait for worker nodes to join.",
                'error': 'NO_ACTORS_AVAILABLE',
                'cluster_status': cluster_status
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
                # Enhanced: get node info from actor response
                print(f"[OK] [NODE - {i}] Response received from actor {i}")
                print(f"[OK] [NODE - {i}] {result['node_label']}: {result['node_hostname']} ({result['node_ip']})")
                print(f"[OK] [NODE - {i}] Model: {result['model_name']}")
                print(f"[OK] [NODE - {i}] Response: {result['response'][:100]}{'...' if len(result['response']) > 100 else ''}")
                
                results.append({
                    'actor_id': i,
                    'response': result['response'],
                    'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    'status': 'success',
                    'node_hostname': result['node_hostname'],
                    'node_ip': result['node_ip'],
                    'node_id': result['node_id'],
                    'node_label': result['node_label'],
                    'model_name': result['model_name'],
                    'processing_time': result['processing_time']
                })
                successful_responses += 1
            except Exception as e:
                print(f"[ERROR] [NODE - {i}] Failed: {e}")
                results.append({
                    'actor_id': i,
                    'response': f"Error: {str(e)}",
                    'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    'status': 'error',
                    'node_hostname': 'unknown',
                    'node_ip': 'unknown',
                    'node_id': 'unknown',
                    'node_label': 'Unknown Node',
                    'model_name': 'unknown',
                    'error': str(e)
                })
        
        # Consolidate results
        consolidated_result = {
            'prompt': prompt,
            'request_timestamp': request_timestamp,
            'total_actors': len(self.actors),
            'successful_responses': successful_responses,
            'results': results,
            'consolidated_response': results[0]['response'] if results else "No responses received",
            'cluster_status': cluster_status
        }
        
        print(f"[OK] Successful Responses: {successful_responses}/{len(self.actors)}")
        
        # Log detailed results with node information
        for result in results:
            if result['status'] == 'success':
                print(f"\n[MODEL: {result['model_name'].upper()}]")
                print(f"   [NODE] {result['node_label']}: {result['node_hostname']} ({result['node_ip']})")
                print(f"   [TIME] Processing: {result['processing_time']:.2f}s")
                print(f"   [RESPONSE] {result['response'][:100]}...")
            else:
                print(f"\n[ERROR] [MODEL: {result['model_name']}]")
                print(f"   [NODE] {result['node_label']}: {result['node_hostname']} ({result['node_ip']})")
                print(f"   [ERROR] {result['response']}")
        
        print(f"\n[OK] [HEAD NODE - REQUEST COMPLETED] All responses logged and consolidated")
        
        return consolidated_result

def run_head_mode(config):
    """Run the cluster coordinator in head mode."""
    print("\n" + "="*80)
    print("🎯 [HEAD NODE STARTING] Distributed Ray Cluster Coordinator")
    print("="*80)
    logger.info("Starting Ray cluster coordinator in head mode")
    
    try:
        # Connect to existing Ray session (started by startup script)
        # Don't provide address or resource arguments when connecting to existing session
        ray.init(
            ignore_reinit_error=True,
            log_to_driver=True
        )
        logger.info("Connected to existing Ray session")
        print("✅ [CLUSTER STATUS] Connected to Ray Cluster Successfully")
        
    except Exception as e:
        print(f"❌ [ERROR] Failed to connect to Ray session: {e}")
        logger.error(f"Failed to connect to Ray session: {e}")
        raise
    
    # Head node no longer loads models - it's a pure coordinator
    print("\n🎯 [COORDINATOR MODE] Head Node is Coordinator Only")
    print("   📡 Waiting for worker nodes to join and register models...")
    print("   🤖 No models loaded on head node (memory optimized)")
    logger.info("Head node running in coordinator mode - no models loaded")
    
    # Create PromptCoordinator that will discover worker actors
    print(f"\n🎯 [REALTIME PROMPT SYSTEM] Initializing Prompt Coordinator...")
    
    # Create the prompt coordinator as a named actor in the default namespace
    # It will start with no actors and discover them as workers join
    try:
        prompt_coordinator = PromptCoordinator.options(
            name="prompt_coordinator", 
            namespace="default",
            lifetime="detached"  # Ensure actor survives head node restarts
        ).remote([])
        
        print(f"✅ Prompt Coordinator created and registered as 'prompt_coordinator'")
        print(f"📡 Coordinator will discover worker actors as they join")
        print(f"🎮 Use real_interactive_prompts.py to send prompts interactively")
        
        # Verify the coordinator is accessible
        try:
            actor_count = ray.get(prompt_coordinator.get_actor_count.remote())
            print(f"✅ Coordinator verification: {actor_count} actors currently registered")
        except Exception as e:
            print(f"⚠️  Coordinator verification failed: {e}")
            
    except Exception as e:
        print(f"❌ [ERROR] Failed to create prompt coordinator: {e}")
        logger.error(f"Failed to create prompt coordinator: {e}")
        raise
    
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
            try:
                cluster_resources = ray.cluster_resources()
                print(f"\n📈 [CLUSTER STATUS] Resources: {cluster_resources}")
                
                # Try to get the coordinator to check available actors
                try:
                    coordinator = ray.get_actor("prompt_coordinator", namespace="default")
                    actor_count = ray.get(coordinator.get_actor_count.remote())
                    print(f"🤖 [ACTOR STATUS] Available inference actors: {actor_count}")
                    
                    # If we have actors, show more details
                    if actor_count > 0:
                        try:
                            actor_info = ray.get(coordinator.get_actor_info.remote())
                            print(f"📊 [ACTOR DETAILS] {actor_info['total_actors']} actors from {len(actor_info['cluster_nodes'])} nodes")
                        except Exception as e:
                            print(f"⚠️  Could not get detailed actor info: {e}")
                            
                except Exception as e:
                    print(f"🤖 [ACTOR STATUS] No actors available yet: {e}")
                    
            except Exception as e:
                print(f"❌ [ERROR] Failed to get cluster status: {e}")
                
    except KeyboardInterrupt:
        print("\n🛑 [SHUTDOWN] Shutting down Ray cluster...")
        try:
            ray.shutdown()
        except:
            pass

def run_worker_mode(config: Dict[str, Any]):
    """Run the application in worker mode."""
    print("\n" + "="*80)
    print("🔧 [WORKER NODE STARTING] Joining Distributed Cluster")
    print("="*80)
    logger.info("Starting Ray worker node")
    
    # Ensure Ray is properly initialized
    try:
        # Check if Ray is already initialized
        ray.get_runtime_context()
        print("✅ Ray already initialized")
    except Exception:
        print("🔄 Initializing Ray connection...")
        # Initialize Ray connection to the cluster
        ray.init(
            address="ray-head:6379",
            namespace="default",
            log_to_driver=True,
            ignore_reinit_error=True
        )
        print("✅ Ray initialized successfully")
    
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
    
    model_names = config.get('models', {}).get('preload', ["gpt2"])  # Simplified to just gpt2 for testing
    actors = []
    
    for model_name in model_names:
        if model_name in MODEL_CONFIGS:
            try:
                actor = LLMInferenceActor.remote(model_name)
                actors.append(actor)
                print(f"   ✅ Created actor for model: {model_name}")
                logger.info(f"Created actor for model: {model_name}")
            except Exception as e:
                print(f"   ❌ Failed to create actor for {model_name}: {e}")
                logger.error(f"Failed to create actor for {model_name}: {e}")
        else:
            print(f"   ⚠️  Unknown model: {model_name}")
            logger.warning(f"Unknown model: {model_name}")
    
    if not actors:
        print("   ❌ No valid models to load")
        logger.error("No valid models to load")
        return
    
    print(f"   📊 Total actors created on worker: {len(actors)}")
    
    # Register actors with the coordinator with improved retry logic
    print(f"\n📡 [ACTOR REGISTRATION] Registering Actors with Coordinator")
    
    # Enhanced retry mechanism for coordinator registration
    max_retries = 10
    retry_delay = 15  # seconds
    registration_success = False
    
    for attempt in range(max_retries):
        try:
            print(f"   [ATTEMPT {attempt + 1}/{max_retries}] Attempting to discover coordinator actor...")
            
            # Wait before trying to connect (longer wait for first few attempts)
            if attempt > 0:
                wait_time = retry_delay + (attempt * 5)  # Progressive backoff
                print(f"   [WAIT] Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            
            # Try to get the coordinator actor
            try:
                coordinator = ray.get_actor("prompt_coordinator", namespace="default")
                print("   ✅ Coordinator actor found!")
            except Exception as e:
                print(f"   ❌ Coordinator actor NOT found: {e}")
                if attempt < max_retries - 1:
                    print(f"   🔄 Will retry in {retry_delay + (attempt * 5)}s...")
                    continue
                else:
                    raise Exception(f"Failed to find coordinator after {max_retries} attempts: {e}")
            
            print(f"   ✅ Found coordinator, registering {len(actors)} actors...")
            
            # Register each actor with individual retry logic
            successful_registrations = 0
            for i, actor in enumerate(actors):
                print(f"   [DEBUG] Registering actor {i+1}/{len(actors)}...")
                actor_retry_count = 0
                actor_max_retries = 3
                
                while actor_retry_count < actor_max_retries:
                    try:
                        actor_id = ray.get(coordinator.register_actor.remote(actor, model_names[i]))
                        print(f"   ✅ Registered actor {i+1}/{len(actors)} with ID: {actor_id}")
                        successful_registrations += 1
                        break
                    except Exception as e:
                        actor_retry_count += 1
                        print(f"   ⚠️  Actor registration attempt {actor_retry_count}/{actor_max_retries} failed: {e}")
                        if actor_retry_count < actor_max_retries:
                            time.sleep(5)  # Short wait between actor retries
                        else:
                            print(f"   ❌ Failed to register actor {i+1}/{len(actors)} after {actor_max_retries} attempts")
                            raise
            
            if successful_registrations == len(actors):
                print(f"   🎯 All {successful_registrations} actors registered successfully!")
                registration_success = True
                
                # Verify registration with coordinator
                try:
                    actor_info = ray.get(coordinator.get_actor_info.remote())
                    print(f"   📊 Coordinator reports {actor_info['total_actors']} total actors available")
                    
                    # Double-check our actors are in the list
                    if actor_info['total_actors'] >= len(actors):
                        print(f"   ✅ Registration verified! Coordinator has {actor_info['total_actors']} actors")
                    else:
                        print(f"   ⚠️  Registration may be incomplete. Expected {len(actors)}, got {actor_info['total_actors']}")
                        
                except Exception as e:
                    print(f"   ⚠️  Could not verify coordinator status: {e}")
                
                break
            else:
                raise Exception(f"Only {successful_registrations}/{len(actors)} actors registered successfully")
                
        except Exception as e:
            print(f"   ❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"   🔄 Will retry in {retry_delay + (attempt * 5)} seconds...")
            else:
                print(f"   ❌ Failed to register actors with coordinator after {max_retries} attempts: {e}")
                print(f"   ⚠️  Actors will work locally but not be coordinated")
                logger.error(f"Failed to register actors with coordinator: {e}")
                break
    
    print(f"\n" + "="*80)
    if registration_success:
        print("🟢 [WORKER NODE READY] Active and Coordinated")
    else:
        print("🟡 [WORKER NODE READY] Active but Not Coordinated")
    print("="*80)
    print(f"✅ Loaded {len(actors)} models and ready for inference")
    print(f"🔄 Worker node will remain active for incoming requests")
    print(f"📊 Models available: {', '.join(model_names)}")
    print(f"📍 Node: {node_info['hostname']} ({node_info['ip_address']})")
    if registration_success:
        print(f"🎯 Status: Coordinated with cluster")
    else:
        print(f"⚠️  Status: Running independently (coordination failed)")
    
    # Keep the worker running with periodic status updates
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
            
            # Periodically check coordinator status
            if registration_success and time.time() % 300 < 30:  # Every ~5 minutes
                try:
                    coordinator = ray.get_actor("prompt_coordinator", namespace="default")
                    actor_info = ray.get(coordinator.get_actor_info.remote())
                    print(f"   📊 Coordinator Status: {actor_info['total_actors']} total actors")
                except Exception as e:
                    print(f"   ⚠️  Coordinator check failed: {e}")
                    
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
    
    # Run in appropriate mode using the new architecture
    if args.mode == 'head':
        run_head_mode(config)
    elif args.mode == 'worker':
        run_worker_mode(config)
    else:
        logger.error(f"Unknown mode: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
