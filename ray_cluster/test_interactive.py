#!/usr/bin/env python3
"""
Non-interactive test version of real_interactive_prompts.py
"""

import ray
import time

def test_interactive_demo():
    print("\n" + "="*80)
    print("🎮 [TEST INTERACTIVE DEMO] Distributed Ray Cluster Client")
    print("="*80)
    
    # Connect to Ray cluster
    print("🔗 Connecting to Ray cluster...")
    try:
        ray.init(address="ray://localhost:10001", namespace="default")
        print("✅ Connected to Ray cluster")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Get the prompt coordinator
    print("🎯 Looking for prompt coordinator...")
    try:
        coordinator = ray.get_actor("prompt_coordinator", namespace="default")
        print("✅ Found prompt coordinator")
    except Exception as e:
        print(f"❌ Failed to find coordinator: {e}")
        return
    
    # Get actor count
    try:
        actor_count = ray.get(coordinator.get_actor_count.remote())
        print(f"🤖 Available inference actors: {actor_count}")
    except Exception as e:
        print(f"❌ Error getting actor count: {e}")
        return
    
    if actor_count == 0:
        print("⚠️  No inference actors available.")
        print("This means no worker nodes are running inference actors.")
        print("The cluster is working, but no models are loaded for inference.")
        return
    
    # Test prompts
    test_prompts = [
        "What is artificial intelligence?",
        "Explain machine learning in simple terms",
        "What is the difference between AI and ML?"
    ]
    
    print(f"\n🧪 Testing {len(test_prompts)} prompts...")
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'='*60}")
        print(f"🧪 [TEST {i}/{len(test_prompts)}] Prompt: '{prompt}'")
        print(f"{'='*60}")
        
        try:
            start_time = time.time()
            result = ray.get(coordinator.process_prompt.remote(prompt))
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
                        print(f"   Model: {response.get('model_name', 'Unknown')}")
                        break
            else:
                print("❌ No successful responses received")
                
        except Exception as e:
            print(f"❌ Error processing prompt: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Interactive demo test completed!")
    print("If you see successful responses, the cluster is working correctly.")
    print("If you see 0 actors, the worker nodes need to be running inference actors.")
    print(f"{'='*60}")
    
    # Cleanup
    try:
        ray.shutdown()
    except:
        pass

if __name__ == "__main__":
    test_interactive_demo() 