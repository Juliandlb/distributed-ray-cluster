#!/usr/bin/env python3
"""
Simple test script to verify the distributed Ray cluster is working
"""

import ray
import time

def test_cluster():
    print("🔗 Connecting to Ray cluster...")
    
    try:
        # Connect to the Ray cluster running in the container
        ray.init(address="ray://localhost:10001", namespace="default")
        print("✅ Connected to Ray cluster")
        
        # Look for the prompt coordinator
        print("🎯 Looking for prompt coordinator...")
        coordinator = ray.get_actor("prompt_coordinator", namespace="default")
        print("✅ Found prompt coordinator")
        
        # Get cluster status
        actor_count = ray.get(coordinator.get_actor_count.remote())
        print(f"🤖 Available inference actors: {actor_count}")
        
        # Test a simple prompt
        test_prompt = "Hello, this is a test of the distributed Ray cluster!"
        print(f"\n🧪 Testing with prompt: '{test_prompt}'")
        
        start_time = time.time()
        result = ray.get(coordinator.process_prompt.remote(test_prompt))
        end_time = time.time()
        
        print(f"📥 Response received in {end_time - start_time:.2f}s")
        print(f"✅ Successful responses: {result.get('successful_responses', 0)}")
        
        if result.get('successful_responses', 0) > 0:
            print(f"💬 Response: {result.get('consolidated_response', 'No response')}")
            
            # Show which nodes responded
            for response in result.get('results', []):
                if response.get('status') == 'success':
                    print(f"🎯 Answered by: {response.get('node_label', 'Unknown')}")
                    print(f"   Hostname: {response.get('node_hostname', 'Unknown')}")
                    print(f"   IP: {response.get('node_ip', 'Unknown')}")
                    break
        else:
            print("❌ No successful responses received")
        
        # Get detailed cluster status
        try:
            cluster_status = ray.get(coordinator.get_cluster_status.remote())
            nodes = cluster_status.get('cluster_nodes', {})
            print(f"\n📊 Cluster has {len(nodes)} nodes:")
            for node_id, node_info in nodes.items():
                status = "🟢" if node_info.get('alive', False) else "🔴"
                print(f"   {status} {node_info.get('label', 'Unknown')} ({node_info.get('hostname', 'Unknown')})")
                print(f"      IP: {node_info.get('ip', 'Unknown')}")
                print(f"      Actors: {node_info.get('actor_count', 0)}")
        except Exception as e:
            print(f"⚠️  Could not get detailed cluster status: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            ray.shutdown()
        except:
            pass

if __name__ == "__main__":
    test_cluster() 