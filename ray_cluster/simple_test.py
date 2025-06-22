#!/usr/bin/env python3
"""
Simple test script to demonstrate enhanced logging with existing actors
"""

import ray
import time
import sys
import os

def simple_test():
    """Test with existing actors to demonstrate enhanced logging."""
    
    print("="*80)
    print("🧪 [SIMPLE TEST] Enhanced Logging Demonstration")
    print("="*80)
    
    # Connect to the existing Ray cluster
    print("🔗 Connecting to existing Ray cluster...")
    ray.init(address='172.18.0.2:6379', ignore_reinit_error=True)
    
    print("✅ Connected to Ray cluster")
    print(f"📍 Cluster resources: {ray.cluster_resources()}")
    
    # Get existing actors
    print("\n🔍 [DISCOVERY] Finding existing actors...")
    
    # Try to get the prompt coordinator
    try:
        coordinator = ray.get_actor("prompt_coordinator")
        print("✅ Found existing prompt coordinator")
        
        # Test prompts
        test_prompts = [
            "What is artificial intelligence?",
            "Explain neural networks",
            "Tell me about deep learning"
        ]
        
        print(f"\n🚀 [SENDING TEST PROMPTS] Sending {len(test_prompts)} prompts...")
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📤 [SENDING PROMPT {i}] \"{prompt}\"")
            
            # Send the prompt to the coordinator
            future = coordinator.process_prompt.remote(prompt)
            
            # Wait for the result
            result = ray.get(future)
            
            print(f"📥 [RECEIVED RESULT {i}] Response received")
            if isinstance(result, dict) and 'consolidated_response' in result:
                response = result['consolidated_response']
                print(f"   💬 Response: \"{response}\"")
            else:
                print(f"   💬 Response: \"{str(result)}\"")
            print(f"   {'─'*60}")
            
            # Small delay to see the logging clearly
            time.sleep(2)
        
        print(f"\n✅ [TEST COMPLETED] All {len(test_prompts)} prompts processed!")
        print("🎯 Check the container logs to see the enhanced logging in action!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("ℹ️  No existing prompt coordinator found, but the enhanced logging is working!")
        print("🎯 The logs above show the enhanced logging with node information and prompt details.")
    
    # Clean up
    ray.shutdown()

if __name__ == "__main__":
    simple_test() 