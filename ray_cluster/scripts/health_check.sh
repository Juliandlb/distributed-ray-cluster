#!/bin/bash

# Health check for Ray processes - check if Ray port is listening
check_ray_port() {
    if netstat -tuln 2>/dev/null | grep ":6379 " > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if Ray is running
if check_ray_port; then
    echo "Ray process is running (port 6379 is listening)"
    exit 0
else
    echo "Ray process is not running (port 6379 is not listening)"
    exit 1
fi 