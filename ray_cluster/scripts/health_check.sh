#!/bin/bash

# Ray API-based health check
python3 - <<'EOF'
import ray
import sys
try:
    if not ray.is_initialized():
        ray.init(address='auto', ignore_reinit_error=True)
    resources = ray.cluster_resources()
    print("✅ Ray is initialized and cluster resources are available:", resources)
    sys.exit(0)
except Exception as e:
    print(f"❌ Ray health check failed: {e}")
    sys.exit(1)
EOF 