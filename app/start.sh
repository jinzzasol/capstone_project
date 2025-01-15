#!/bin/sh
# start.sh

# Function to handle process termination
cleanup() {
    echo "Received stop signal, shutting down gracefully..."
    kill -TERM "$child"
    wait "$child"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start Gunicorn in the background
gunicorn app:app &

# Store the process ID
child=$!

# Wait for the process to terminate
wait "$child"
