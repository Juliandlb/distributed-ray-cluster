#!/usr/bin/env python3
"""
Test script to send prompts to the distributed Ray cluster
and observe the enhanced logging across nodes.
"""

import ray
import time
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import LLMInferenceActor

def test_distributed_inference():
    """Test distributed inference with enhanced logging."""
    
    print("="*80)
    print("🧪 [TESTING] Distributed Inference with Enhanced Logging")
    print("="*80)
    
    # Connect to the existing Ray cluster
    print("🔗 Connecting to existing Ray cluster...")
    ray.init(address='172.18.0.2:6379', ignore_reinit_error=True)
    
    print("✅ Connected to Ray cluster")
    print(f"📍 Cluster resources: {ray.cluster_resources()}")
    
    # Get all actors in the cluster
    print("\n🔍 [DISCOVERY] Finding all actors in the cluster...")
    
    # We'll create a new actor to test the enhanced logging
    print("\n🤖 [CREATING TEST ACTOR] Creating a new actor for testing...")
    test_actor = LLMInferenceActor.remote("tiny-gpt2")
    
    # Test prompts
    test_prompts = [
        "What is artificial intelligence?",
        "Explain neural networks",
        "Tell me about deep learning",
        "What is natural language processing?",
        "Explain computer vision"
    ]
    
    print(f"\n🚀 [SENDING TEST PROMPTS] Sending {len(test_prompts)} prompts...")
    
    # Send prompts one by one to see the enhanced logging
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📤 [SENDING PROMPT {i}] \"{prompt}\"")
        
        # Send the prompt
        future = test_actor.generate.remote(prompt)
        
        # Wait for the result
        result = ray.get(future)
        
        print(f"📥 [RECEIVED RESULT {i}] Response received")
        print(f"   💬 Response: \"{result}\"")
        print(f"   {'─'*60}")
        
        # Small delay to see the logging clearly
        time.sleep(2)
    
    print(f"\n✅ [TEST COMPLETED] All {len(test_prompts)} prompts processed!")
    print("🎯 Check the container logs to see the enhanced logging in action!")
    
    # Clean up
    ray.shutdown()

if __name__ == "__main__":
    test_distributed_inference() 