#!/bin/bash

# Health check for Ray processes
check_ray_process() {
    if pgrep -f "ray.*start" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if Ray is running
if check_ray_process; then
    echo "Ray process is running"
    exit 0
else
    echo "Ray process is not running"
    exit 1
fi 