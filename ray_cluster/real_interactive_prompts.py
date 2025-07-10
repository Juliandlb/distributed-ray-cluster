#!/usr/bin/env python3
"""
Real Interactive Prompt Interface
Connects to actual Ray cluster and performs real inference!
"""

import ray
import time
import asyncio
from datetime import datetime

@ray.remote
class InteractivePromptClient:
    """Client for interactive prompt processing."""
    
    def __init__(self):
        self.prompt_count = 0
        self.coordinator = None
        
    def connect_to_coordinator(self):
        """Connect to the prompt coordinator."""
        try:
            # Try to get the coordinator actor with namespace
            self.coordinator = ray.get_actor("prompt_coordinator", namespace="default")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to coordinator: {e}")
            return False
    
    def get_cluster_status(self):
        """Get current cluster status."""
        try:
            if self.coordinator:
                actor_count = ray.get(self.coordinator.get_actor_count.remote())
                return f"Connected to coordinator with {actor_count} inference actors"
            else:
                return "Not connected to coordinator"
        except Exception as e:
            return f"Error getting status: {e}"
    
    def process_prompt(self, prompt):
        """Process a prompt through the coordinator."""
        try:
            if not self.coordinator:
                return "❌ Not connected to coordinator"
            
            # Send prompt to coordinator
            result = ray.get(self.coordinator.process_prompt.remote(prompt))
            self.prompt_count += 1
            return result
            
        except Exception as e:
            return f"❌ Error processing prompt: {e}"

def display_cluster_status(coordinator):
    """Display comprehensive cluster status"""
    try:
        cluster_status = ray.get(coordinator.get_cluster_status.remote())
        
        print("\n" + "="*60)
        print("📊 [CLUSTER STATUS] Distributed Ray Cluster")
        print("="*60)
        
        # Cluster resources
        resources = cluster_status['cluster_resources']
        print(f"🔧 [RESOURCES]")
        print(f"   CPU: {resources.get('CPU', 0):.1f}")
        print(f"   Memory: {resources.get('memory', 0) / 1024 / 1024 / 1024:.1f} GB")
        
        # Cluster nodes
        nodes = cluster_status['cluster_nodes']
        print(f"\n🖥️  [NODES] Total: {len(nodes)}")
        for node_id, node_info in nodes.items():
            status = "🟢" if node_info['alive'] else "🔴"
            print(f"   {status} {node_info['label']} ({node_info['hostname']})")
            print(f"      IP: {node_info['ip']}")
            print(f"      Actors: {node_info['actor_count']}")
            print(f"      Resources: CPU={node_info['resources'].get('CPU', 0):.1f}, Memory={node_info['resources'].get('memory', 0) / 1024 / 1024 / 1024:.1f}GB")
        
        # Actor details
        actors = cluster_status['actor_details']
        print(f"\n🤖 [ACTORS] Total: {len(actors)}")
        for actor_id, actor_info in actors.items():
            print(f"   Actor {actor_id}: {actor_info['model_name']} on {actor_info['node_label']}")
        
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error getting cluster status: {e}")

def process_prompt_with_node_info(coordinator, prompt):
    """Process a prompt and display detailed node information"""
    try:
        print(f"\n🤖 [PROMPT] '{prompt}'")
        print(f"📤 [SENDING] Sending to coordinator...")
        
        start_time = time.time()
        result = ray.get(coordinator.process_prompt.remote(prompt))
        end_time = time.time()
        
        print(f"📥 [RESPONSE] Received in {end_time - start_time:.2f}s")
        
        # Display cluster information
        cluster_status = result.get('cluster_status', {})
        print(f"\n📊 [CLUSTER INFO]")
        print(f"   Total nodes: {len(cluster_status.get('cluster_nodes', {}))}")
        print(f"   Total actors: {result['total_actors']}")
        print(f"   Successful responses: {result['successful_responses']}")
        
        # Display results with node information
        print(f"\n💬 [RESPONSES]")
        for i, response in enumerate(result['results']):
            if response['status'] == 'success':
                print(f"   ✅ Actor {response['actor_id']} ({response['model_name']})")
                print(f"      {response['node_label']}: {response['node_hostname']} ({response['node_ip']})")
                print(f"      Processing time: {response['processing_time']:.2f}s")
                print(f"      Response: {response['response'][:200]}{'...' if len(response['response']) > 200 else ''}")
            else:
                print(f"   ❌ Actor {response['actor_id']} - Error: {response['response']}")
        
        # Show which node answered (for single response)
        if result['successful_responses'] == 1:
            for response in result['results']:
                if response['status'] == 'success':
                    print(f"\n🎯 [ANSWERED BY] {response['node_label']}")
                    print(f"   Hostname: {response['node_hostname']} ({response['node_ip']})")
                    print(f"   Model: {response['model_name']}")
                    print(f"   Processing time: {response['processing_time']:.2f}s")
                    break
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing prompt: {e}")
        return None

def real_interactive_prompts():
    """Real interactive prompt interface using actual Ray cluster."""
    print("\n" + "="*80)
    print("🎮 [REAL INTERACTIVE PROMPTS] Distributed Ray Cluster Client")
    print("="*80)
    
    # Connect to Ray cluster with improved error handling
    print("🔗 Connecting to Ray cluster...")
    max_connection_attempts = 5
    connection_attempt = 0
    
    while connection_attempt < max_connection_attempts:
        try:
            print(f"   [ATTEMPT {connection_attempt + 1}/{max_connection_attempts}] Connecting to ray://52.224.243.185:10001...")
            
            # Initialize Ray connection with better configuration
            ray.init(
                address="ray://52.224.243.185:10001", 
                namespace="default",
                log_to_driver=False,  # Reduce log noise
                ignore_reinit_error=True
            )
            print("✅ Connected to Ray cluster")
            break
            
        except Exception as e:
            connection_attempt += 1
            print(f"❌ Connection attempt {connection_attempt} failed: {e}")
            
            if connection_attempt < max_connection_attempts:
                wait_time = connection_attempt * 10  # Progressive backoff
                print(f"   [WAIT] Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"❌ Failed to connect to Ray cluster after {max_connection_attempts} attempts")
                print("   Please ensure the cluster is running and accessible")
        return
    
    # Get the prompt coordinator with retry logic
    print("🎯 [COORDINATOR] Looking for prompt coordinator...")
    max_coordinator_attempts = 10
    coordinator_attempt = 0
    coordinator = None
    
    while coordinator_attempt < max_coordinator_attempts:
        try:
            print(f"   [ATTEMPT {coordinator_attempt + 1}/{max_coordinator_attempts}] Looking for coordinator...")
            coordinator = ray.get_actor("prompt_coordinator", namespace="default")
            print("✅ Found prompt coordinator")
            break
            
        except Exception as e:
            coordinator_attempt += 1
            print(f"❌ Coordinator attempt {coordinator_attempt} failed: {e}")
            
            if coordinator_attempt < max_coordinator_attempts:
                wait_time = coordinator_attempt * 5  # Shorter waits for coordinator
                print(f"   [WAIT] Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"❌ Could not find prompt coordinator after {max_coordinator_attempts} attempts")
                print("⚠️  Running in simulation mode")
                coordinator = None
                break
    
    if coordinator:
        # Get initial actor count
        try:
            actor_count = ray.get(coordinator.get_actor_count.remote())
            print(f"🤖 Available inference actors: {actor_count}")
            
            if actor_count == 0:
                print("⚠️  No actors available. Please wait for worker nodes to join and register.")
                print("   You can still use the interface, but responses will be simulated.")
            else:
                # Get detailed actor information
                try:
                    actor_info = ray.get(coordinator.get_actor_info.remote())
                    print(f"📊 Cluster has {actor_info['total_actors']} actors from {len(actor_info['cluster_nodes'])} nodes")
                except Exception as e:
                    print(f"⚠️  Could not get detailed actor info: {e}")
        
        except Exception as e:
            print(f"❌ Error getting actor count: {e}")
            print("⚠️  Running in simulation mode")
            coordinator = None
    
    print("\n" + "="*80)
    print("🎮 [INTERACTIVE MODE] Type your prompts below")
    print("="*80)
    print("Commands:")
    print("  - Type any prompt and press Enter")
    print("  - 'status' - Show cluster status and node information")
    print("  - 'actors' - Show available actors")
    print("  - 'test' - Run a test prompt")
    print("  - 'quit' or 'exit' - Exit the interface")
    print("="*80)
    
    while True:
        try:
            # Get user input
            user_input = input("\n🤖 [PROMPT] ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'status':
                if coordinator:
                    display_cluster_status(coordinator)
                else:
                    print("❌ Coordinator not available")
                continue
            elif user_input.lower() == 'actors':
                if coordinator:
                    try:
                        actor_info = ray.get(coordinator.get_actor_info.remote())
                        print(f"\n🤖 [ACTORS] Total: {actor_info['total_actors']}")
                        for actor_id, info in actor_info['actors'].items():
                            print(f"   Actor {actor_id}: {info['model_name']} on {info['node_label']}")
                    except Exception as e:
                        print(f"❌ Error getting actor info: {e}")
                else:
                    print("❌ Coordinator not available")
                continue
            elif user_input.lower() == 'test':
                user_input = "What is artificial intelligence?"
                print(f"🧪 [TEST] Using prompt: '{user_input}'")
            
            # Process the prompt
            if coordinator:
                result = process_prompt_with_node_info(coordinator, user_input)
                if result and result['successful_responses'] > 0:
                    print(f"\n💬 [FINAL RESPONSE] {result['consolidated_response']}")
                else:
                    print("❌ No successful responses received")
            else:
                # Fallback to simulation
                print("📤 [SENDING] (simulation mode)")
                time.sleep(1)
                print("📥 [RESPONSE] (simulation mode)")
                print("💬 [RESPONSE] This is a simulated response since no coordinator is available.")
                print("   Please ensure the cluster is running and workers have registered.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Cleanup
    try:
        ray.shutdown()
    except:
        pass

if __name__ == "__main__":
    real_interactive_prompts() 