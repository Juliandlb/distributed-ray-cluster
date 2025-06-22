#!/usr/bin/env python3
"""
Real-time Interactive Client for Distributed Ray Cluster
Allows users to type prompts and see responses in real-time
"""

import ray
import time
import sys
import os
import threading
from datetime import datetime

def realtime_client():
    """Real-time interactive client for distributed inference."""
    
    print("="*80)
    print("🎮 [REALTIME CLIENT] Interactive Distributed Inference")
    print("="*80)
    
    # Connect to the existing Ray cluster
    print("🔗 Connecting to Ray cluster...")
    try:
        ray.init(address='172.18.0.2:6379', ignore_reinit_error=True)
        print("✅ Connected to Ray cluster")
        print(f"📍 Cluster resources: {ray.cluster_resources()}")
    except Exception as e:
        print(f"❌ Failed to connect to Ray cluster: {e}")
        return
    
    # Try to get existing actors or create new ones
    print("\n🔍 [DISCOVERY] Looking for existing actors...")
    
    try:
        # Try to get existing prompt coordinator
        coordinator = ray.get_actor("prompt_coordinator")
        print("✅ Found existing prompt coordinator")
    except:
        print("⚠️  No existing prompt coordinator found")
        print("🔄 Creating new actors for real-time inference...")
        
        # Create a simple actor for real-time inference
        from main import LLMInferenceActor
        
        # Create a single actor for real-time inference
        actor = LLMInferenceActor.remote("tiny-gpt2")
        print("✅ Created inference actor")
        
        # Simple function to process prompts
        def process_prompt_simple(prompt):
            try:
                result = ray.get(actor.generate.remote(prompt))
                return result
            except Exception as e:
                return f"Error: {str(e)}"
    
    print("\n" + "="*80)
    print("🎯 [READY] Real-time inference system ready!")
    print("="*80)
    print("💡 Type your prompts and press Enter to get responses")
    print("💡 Type 'quit' or 'exit' to stop")
    print("💡 Type 'status' to see cluster status")
    print("="*80)
    
    # Real-time prompt loop
    prompt_count = 0
    
    while True:
        try:
            # Get user input
            prompt = input(f"\n🤖 [PROMPT {prompt_count + 1}] ").strip()
            
            if not prompt:
                continue
                
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("\n👋 [GOODBYE] Shutting down real-time client...")
                break
                
            if prompt.lower() == 'status':
                print(f"\n📊 [CLUSTER STATUS]")
                print(f"   Resources: {ray.cluster_resources()}")
                print(f"   Nodes: {len([k for k in ray.cluster_resources().keys() if k.startswith('node:')])}")
                continue
            
            # Process the prompt
            print(f"📤 [SENDING] '{prompt}'")
            start_time = time.time()
            
            try:
                if 'coordinator' in locals():
                    # Use existing coordinator
                    future = coordinator.process_prompt.remote(prompt)
                    result = ray.get(future)
                    if isinstance(result, dict) and 'consolidated_response' in result:
                        response = result['consolidated_response']
                    else:
                        response = str(result)
                else:
                    # Use simple actor
                    response = process_prompt_simple(prompt)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                print(f"📥 [RESPONSE] (took {processing_time:.2f}s)")
                print(f"💬 '{response}'")
                print(f"⏱️  Processing time: {processing_time:.2f} seconds")
                
                prompt_count += 1
                
            except Exception as e:
                print(f"❌ [ERROR] Failed to process prompt: {e}")
                print("💡 Try again or check cluster status with 'status'")
                
        except KeyboardInterrupt:
            print("\n\n👋 [GOODBYE] Shutting down real-time client...")
            break
        except EOFError:
            print("\n\n👋 [GOODBYE] Shutting down real-time client...")
            break
    
    # Cleanup
    print("🧹 Cleaning up...")
    ray.shutdown()
    print("✅ Real-time client stopped")

if __name__ == "__main__":
    realtime_client() 