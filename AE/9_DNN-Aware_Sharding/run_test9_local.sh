#!/bin/bash
source settings/config.sh

set -e  # Exit on error

mkdir -p tmp
rm -rf tmp/test9
mkdir -p tmp/test9

echo "Cleaning up /dev/shm..."
find /dev/shm/* -writable -exec rm -rf {} + 2>/dev/null  || true
sleep 5

cleanup() {
    # Cleanup all processes
    echo "Cleaning up all background processes..."
    for pid in "${SERVER_PIDS[@]}"; do
        if kill -0 $pid 2>/dev/null; then
            kill -9 $pid
            sleep 2
        fi
    done

    for pid in $PID_STORAGE; do
        if kill -0 $pid 2>/dev/null; then
            kill -9 $pid
            sleep 2
        fi
    done

    wait
    echo "All processes finished and cleaned up."

    # Step 11: Stop storage
    find /dev/shm/* -writable -exec rm -rf {} + 2>/dev/null
}

# Trap SIGINT (Ctrl+C) and call cleanup function
trap cleanup SIGINT
trap cleanup EXIT

# Step 0: Generate bins
mkdir -p build/test9
python ./source/storage_client/generate_bins.py build/test9

# Step 2: storage
echo "Starting storage..."
STORAGE_PORT=$GLOBAL_STORAGE_PORT
./build/bin/storage $STORAGE_PORT $STORAGE_PORT 30 > tmp/test9/log_storage.txt 2>&1 &
PID_STORAGE=$!

# Step 3: deploy
echo "Deploying..."
./build/bin/shard_deploy 

# Step 4: start client
echo "Starting client..."

CLIENT_LIST="0 1"

PID_SERVERS=()
for CLIENT in $CLIENT_LIST;
do
    echo "Starting client $CLIENT..."
    ./build/bin/shard_cli $CLIENT $GLOBAL_CONTROLLER_IP $GLOBAL_CONTROLLER_PORT_FOR_SUBSCRIBER 10 > tmp/test9/log_client_$CLIENT.txt 2>&1 &
    SERVER_PIDS+=($!)
    sleep 1
done

# Step 5: start controller
echo "Starting controller..."
./build/bin/shard_ctl 2 $GLOBAL_CONTROLLER_PORT_FOR_SUBSCRIBER | tee tmp/test9/log_controller.txt
