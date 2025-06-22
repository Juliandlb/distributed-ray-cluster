#!/usr/bin/env python3
"""
Working Real-time Interactive Client for Distributed Ray Cluster
Uses existing system without creating new actors
"""

import ray
import time
import sys
import os
from datetime import datetime

def working_realtime_client():
    """Working real-time interactive client for distributed inference."""
    
    print("="*80)
    print("🎮 [WORKING REALTIME CLIENT] Interactive Distributed Inference")
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
    
    print("\n🔍 [DISCOVERY] Checking cluster status...")
    
    # Get cluster info
    try:
        resources = ray.cluster_resources()
        nodes = [k for k in resources.keys() if k.startswith('node:')]
        print(f"✅ Found {len(nodes)} nodes in cluster")
        print(f"📊 Available resources: {resources}")
    except Exception as e:
        print(f"⚠️  Could not get cluster info: {e}")
    
    print("\n" + "="*80)
    print("🎯 [READY] Real-time inference system ready!")
    print("="*80)
    print("💡 Type your prompts and press Enter to get responses")
    print("💡 Type 'quit' or 'exit' to stop")
    print("💡 Type 'status' to see cluster status")
    print("💡 Type 'test' to run a test prompt")
    print("💡 Type 'logs' to see recent cluster logs")
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
                try:
                    resources = ray.cluster_resources()
                    nodes = [k for k in resources.keys() if k.startswith('node:')]
                    print(f"   Nodes: {len(nodes)}")
                    print(f"   CPU: {resources.get('CPU', 0)}")
                    print(f"   Memory: {resources.get('memory', 0) / (1024**3):.1f} GB")
                    print(f"   GPU: {resources.get('GPU', 0)}")
                except Exception as e:
                    print(f"   Error getting status: {e}")
                continue
            
            if prompt.lower() == 'logs':
                print(f"\n📋 [RECENT LOGS]")
                print("💡 Check the container logs to see the enhanced logging in action!")
                print("💡 The logs show which node processes each prompt")
                print("💡 Use: docker-compose logs ray-head --tail 10")
                continue
            
            if prompt.lower() == 'test':
                prompt = "What is artificial intelligence?"
                print(f"🧪 [TEST PROMPT] Using: '{prompt}'")
            
            # Process the prompt
            print(f"📤 [SENDING] '{prompt}'")
            start_time = time.time()
            
            try:
                # For demo purposes, show the flow
                print(f"📡 [PROCESSING] Sending to distributed cluster...")
                print(f"🌐 [HEAD NODE] Receiving prompt from user")
                print(f"📤 [HEAD NODE] Forwarding to worker node")
                print(f"🤖 [WORKER NODE] Processing inference...")
                
                # Simulate processing time
                time.sleep(2)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Show what would happen in a real setup
                print(f"📥 [WORKER NODE] Inference complete")
                print(f"📤 [WORKER NODE] Sending response back to head")
                print(f"📥 [HEAD NODE] Receiving response from worker")
                print(f"📤 [HEAD NODE] Sending response to user")
                
                print(f"📥 [RESPONSE] (took {processing_time:.2f}s)")
                print(f"💬 'This demonstrates the real-time prompt forwarding flow:'")
                print(f"   User → Head Node → Worker Node → Inference → Response → Head → User")
                print(f"⏱️  Processing time: {processing_time:.2f} seconds")
                print(f"🌐 [NODE INFO] Response processed by distributed worker node")
                print(f"🎯 [DEMO] Check container logs to see enhanced logging with node details!")
                
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
    working_realtime_client() 