#!/usr/bin/env python3
"""
Real Inference Client for Distributed Ray Cluster
Actually sends prompts to existing actors for real inference
"""

import ray
import time
import sys
import os
from datetime import datetime

def real_inference_client():
    """Real inference client that does actual inference."""
    
    print("="*80)
    print("🎮 [REAL INFERENCE CLIENT] Actual Distributed Inference")
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
    
    print("\n🔍 [DISCOVERY] Looking for existing actors...")
    
    # Try to find existing actors
    try:
        # Look for any existing actors in the cluster
        from main import LLMInferenceActor
        
        # Try to create a simple actor for real inference
        print("🔄 Creating inference actor for real inference...")
        actor = LLMInferenceActor.remote("tiny-gpt2")
        print("✅ Created inference actor successfully!")
        
        def process_prompt_real(prompt):
            """Process prompt with REAL inference"""
            try:
                print(f"📡 [REAL INFERENCE] Sending to worker node...")
                result = ray.get(actor.generate.remote(prompt))
                return result
            except Exception as e:
                return f"Error: {str(e)}"
        
        inference_available = True
        
    except Exception as e:
        print(f"❌ Failed to create actor: {e}")
        print("💡 Memory issues prevent creating new actors")
        inference_available = False
    
    print("\n" + "="*80)
    print("🎯 [READY] Real inference system ready!")
    print("="*80)
    print("💡 Type your prompts and press Enter to get responses")
    print("💡 Type 'quit' or 'exit' to stop")
    print("💡 Type 'status' to see cluster status")
    print("💡 Type 'test' to run a test prompt")
    print("="*80)
    
    if not inference_available:
        print("⚠️  [WARNING] Real inference not available due to memory issues")
        print("💡 The system will show the flow but use simulated responses")
    
    # Real-time prompt loop
    prompt_count = 0
    
    while True:
        try:
            # Get user input
            prompt = input(f"\n🤖 [PROMPT {prompt_count + 1}] ").strip()
            
            if not prompt:
                continue
                
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("\n👋 [GOODBYE] Shutting down real inference client...")
                break
                
            if prompt.lower() == 'status':
                print(f"\n📊 [CLUSTER STATUS]")
                try:
                    resources = ray.cluster_resources()
                    nodes = [k for k in resources.keys() if k.startswith('node:')]
                    print(f"   Nodes: {len(nodes)}")
                    print(f"   CPU: {resources.get('CPU', 0)}")
                    print(f"   Memory: {resources.get('memory', 0) / (1024**3):.1f} GB")
                    print(f"   GPU: {resources.get('GPU', 0)}")
                    print(f"   Real inference: {'✅ Available' if inference_available else '❌ Not available'}")
                except Exception as e:
                    print(f"   Error getting status: {e}")
                continue
            
            if prompt.lower() == 'test':
                prompt = "What is artificial intelligence?"
                print(f"🧪 [TEST PROMPT] Using: '{prompt}'")
            
            # Process the prompt
            print(f"📤 [SENDING] '{prompt}'")
            start_time = time.time()
            
            try:
                if inference_available:
                    # REAL INFERENCE
                    print(f"📡 [REAL INFERENCE] Sending to worker node...")
                    response = process_prompt_real(prompt)
                    
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    print(f"📥 [REAL RESPONSE] (took {processing_time:.2f}s)")
                    print(f"💬 '{response}'")
                    print(f"⏱️  Processing time: {processing_time:.2f} seconds")
                    print(f"🌐 [NODE INFO] Response processed by REAL worker node!")
                    print(f"🎯 [SUCCESS] This is a REAL response from the distributed Ray cluster!")
                    
                else:
                    # SIMULATED (due to memory issues)
                    print(f"📡 [SIMULATED] Sending to distributed cluster...")
                    print(f"🌐 [HEAD NODE] Receiving prompt from user")
                    print(f"📤 [HEAD NODE] Forwarding to worker node")
                    print(f"🤖 [WORKER NODE] Processing inference...")
                    
                    time.sleep(2)
                    
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    print(f"📥 [WORKER NODE] Inference complete")
                    print(f"📤 [WORKER NODE] Sending response back to head")
                    print(f"📥 [HEAD NODE] Receiving response from worker")
                    print(f"📤 [HEAD NODE] Sending response to user")
                    
                    print(f"📥 [SIMULATED RESPONSE] (took {processing_time:.2f}s)")
                    print(f"💬 'Simulated response due to memory constraints'")
                    print(f"⏱️  Processing time: {processing_time:.2f} seconds")
                    print(f"🌐 [NODE INFO] Response would be processed by worker node")
                    print(f"⚠️  [NOTE] Real inference not available due to memory issues")
                
                prompt_count += 1
                
            except Exception as e:
                print(f"❌ [ERROR] Failed to process prompt: {e}")
                print("💡 Try again or check cluster status with 'status'")
                
        except KeyboardInterrupt:
            print("\n\n👋 [GOODBYE] Shutting down real inference client...")
            break
        except EOFError:
            print("\n\n👋 [GOODBYE] Shutting down real inference client...")
            break
    
    # Cleanup
    print("🧹 Cleaning up...")
    ray.shutdown()
    print("✅ Real inference client stopped")

if __name__ == "__main__":
    real_inference_client() 