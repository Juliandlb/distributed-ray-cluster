#!/usr/bin/env python3
"""
API Server for Distributed Ray Cluster
Provides REST endpoints for real-time inference requests
"""

from flask import Flask, request, jsonify
import ray
import threading
import time
import logging
import os
from datetime import datetime
from main import LLMInferenceActor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables
ray_initialized = False
available_actors = []

def initialize_ray():
    """Initialize Ray connection"""
    global ray_initialized
    try:
        ray_address = os.getenv('RAY_ADDRESS', 'ray-head-service.ray-cluster.svc.cluster.local:6379')
        logger.info(f"Connecting to Ray cluster at: {ray_address}")
        
        ray.init(address=ray_address, ignore_reinit_error=True)
        ray_initialized = True
        logger.info("Successfully connected to Ray cluster")
        
        # Get cluster resources
        resources = ray.cluster_resources()
        logger.info(f"Cluster resources: {resources}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Ray cluster: {e}")
        return False

def get_available_actors():
    """Get available inference actors"""
    global available_actors
    try:
        # Get all actors in the cluster
        actors = ray.get_runtime_context().get_actor_handles()
        available_actors = list(actors.values())
        logger.info(f"Found {len(available_actors)} available actors")
        return available_actors
    except Exception as e:
        logger.error(f"Failed to get actors: {e}")
        return []

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        if not ray_initialized:
            return jsonify({
                'status': 'unhealthy',
                'error': 'Ray not initialized',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        # Check Ray cluster status
        resources = ray.cluster_resources()
        actors = get_available_actors()
        
        return jsonify({
            'status': 'healthy',
            'ray_initialized': ray_initialized,
            'cluster_resources': dict(resources),
            'available_actors': len(actors),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/inference', methods=['POST'])
def inference():
    """Real-time inference endpoint"""
    try:
        if not ray_initialized:
            return jsonify({
                'error': 'Ray cluster not available',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        prompt = data.get('prompt', '')
        if not prompt:
            return jsonify({
                'error': 'No prompt provided',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Get available actors
        actors = get_available_actors()
        if not actors:
            return jsonify({
                'error': 'No inference actors available',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        # Round-robin selection (simple load balancing)
        actor = actors[0]  # For demo, use first available actor
        
        logger.info(f"Processing prompt: {prompt[:50]}...")
        start_time = time.time()
        
        # Submit inference task
        future = actor.generate.remote(prompt)
        result = ray.get(future)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"Inference completed in {processing_time:.2f}s")
        
        return jsonify({
            'prompt': prompt,
            'response': result,
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/cluster/status', methods=['GET'])
def cluster_status():
    """Get detailed cluster status"""
    try:
        if not ray_initialized:
            return jsonify({
                'error': 'Ray not initialized',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        resources = ray.cluster_resources()
        nodes = ray.nodes()
        actors = get_available_actors()
        
        return jsonify({
            'resources': dict(resources),
            'nodes': nodes,
            'available_actors': len(actors),
            'ray_initialized': ray_initialized,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Cluster status failed: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/cluster/scale', methods=['POST'])
def scale_workers():
    """Scale worker nodes (for future use)"""
    try:
        data = request.get_json()
        replicas = data.get('replicas', 1)
        
        # This would integrate with Kubernetes API to scale deployments
        # For now, return a placeholder response
        return jsonify({
            'message': f'Scaling to {replicas} replicas (not implemented yet)',
            'replicas': replicas,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Scale operation failed: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'service': 'Distributed Ray Inference API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'inference': '/inference',
            'cluster_status': '/cluster/status',
            'scale': '/cluster/scale'
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Starting Ray API Server...")
    
    # Initialize Ray connection
    if initialize_ray():
        logger.info("Ray API Server started successfully")
        app.run(host='0.0.0.0', port=8000, debug=False)
    else:
        logger.error("Failed to initialize Ray, exiting")
        exit(1) 