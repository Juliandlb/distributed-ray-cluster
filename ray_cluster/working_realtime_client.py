#!/usr/bin/env python3
"""
Working Real-time Interactive Client for Distributed Ray Cluster
Uses the new coordinator architecture for real inference
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
    
    # Try to get the coordinator
    print("\n🎯 [COORDINATOR] Looking for prompt coordinator...")
    try:
        coordinator = ray.get_actor("prompt_coordinator")
        print("✅ Found prompt coordinator")
        
        # Get initial actor count
        actor_count = ray.get(coordinator.get_actor_count.remote())
        print(f"🤖 Available inference actors: {actor_count}")
        
        if actor_count == 0:
            print("⚠️  No inference actors available yet")
            print("💡 Wait for worker nodes to join and register their models")
        
    except Exception as e:
        print(f"❌ Could not find prompt coordinator: {e}")
        print("💡 Make sure the head node is running in coordinator mode")
        return
    
    print("\n" + "="*80)
    print("🎯 [READY] Real-time inference system ready!")
    print("="*80)
    print("💡 Type your prompts and press Enter to get responses")
    print("💡 Type 'quit' or 'exit' to stop")
    print("💡 Type 'status' to see cluster status")
    print("💡 Type 'actors' to see available inference actors")
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
                    
                    # Get actor count
                    actor_count = ray.get(coordinator.get_actor_count.remote())
                    print(f"   Inference Actors: {actor_count}")
                    
                except Exception as e:
                    print(f"   Error getting status: {e}")
                continue
            
            if prompt.lower() == 'actors':
                print(f"\n🤖 [ACTOR STATUS]")
                try:
                    actor_info = ray.get(coordinator.get_actor_info.remote())
                    print(f"   Total Actors: {actor_info['total_actors']}")
                    print(f"   Actor Keys: {actor_info['actor_keys']}")
                    print(f"   Coordinator Node: {actor_info['node_info']['hostname']}")
                except Exception as e:
                    print(f"   Error getting actor info: {e}")
                continue
            
            if prompt.lower() == 'logs':
                print(f"\n📋 [RECENT LOGS]")
                print("💡 Check the container logs to see the enhanced logging in action!")
                print("💡 The logs show which node processes each prompt")
                print("💡 Use: docker-compose logs ray-head --tail 10")
                print("💡 Use: docker-compose logs ray-worker-1 --tail 10")
                continue
            
            if prompt.lower() == 'test':
                prompt = "What is artificial intelligence?"
                print(f"🧪 [TEST PROMPT] Using: '{prompt}'")
            
            # Process the prompt
            print(f"📤 [SENDING] '{prompt}'")
            start_time = time.time()
            
            try:
                # Send to coordinator for real inference
                print(f"📡 [PROCESSING] Sending to coordinator...")
                result = ray.get(coordinator.process_prompt.remote(prompt))
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Display results
                print(f"📥 [RESPONSE] (took {processing_time:.2f}s)")
                print(f"🤖 [ACTORS] Used {result['successful_responses']}/{result['total_actors']} actors")
                
                if result.get('error') == 'NO_ACTORS_AVAILABLE':
                    print(f"⚠️  No inference actors available")
                    print(f"💡 Wait for worker nodes to join and register their models")
                else:
                    print(f"💬 [RESPONSE] {result['consolidated_response']}")
                    
                    # Show detailed results if multiple actors
                    if len(result['results']) > 1:
                        print(f"\n📊 [DETAILED RESULTS]")
                        for i, res in enumerate(result['results']):
                            status = "✅" if res['status'] == 'success' else "❌"
                            print(f"   {status} Actor {res['actor_id']}: {res['response'][:50]}...")
                
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