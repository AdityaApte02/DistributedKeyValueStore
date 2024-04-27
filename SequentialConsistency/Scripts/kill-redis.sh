#!/bin/bash

# Find the PIDs of all redis-server processes
redis_pids=$(pgrep redis-server)

if [ -z "$redis_pids" ]; then
    echo "No redis-server processes found."
    exit 1
fi

# Kill all redis-server processes
echo "Killing redis-server processes..."
for pid in $redis_pids; do
    kill "$pid"
done

echo "Redis-server processes killed successfully."
