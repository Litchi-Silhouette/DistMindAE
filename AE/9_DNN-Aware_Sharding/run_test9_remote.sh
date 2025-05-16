#!/bin/bash
source settings/config.sh

set -e  # Exit on error

mkdir -p tmp
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp --test_index 9
rm -rf tmp/test9
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp/test9 --test_index 9 --stop
mkdir -p tmp/test9
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp/test9 --test_index 9
sleep 5

echo "Cleaning up /dev/shm..."
python ./source/py_utils/launch_remote.py --launch_part cleanup --test_index 1
sleep 5

cleanup() {
    # Cleanup all processes
    echo "Cleaning up all background processes..."
    python ./source/py_utils/launch_remote.py --launch_part storage_client --test_index 9--stop 
    sleep 5

    python ./source/py_utils/launch_remote.py --launch_part dist_storage --test_index 9--stop
    sleep 5

    wait
    echo "All processes finished and cleaned up."

    # Step 11: Stop storage
    python ./source/py_utils/launch_remote.py --launch_part cleanup --test_index 1
}

# Trap SIGINT (Ctrl+C) and call cleanup function
trap cleanup SIGINT
trap cleanup EXIT

# Step 0: Generate bins
mkdir -p build/test9
python ./source/storage_client/generate_bins.py build/test9


# Step 2: Storage
echo "Starting storage..."
python ./source/py_utils/launch_remote.py --launch_part dist_storage --test_index 9--log_file tmp/test9/log_storage.txt
sleep 5  # Give storage a bit of head start

# Step 3: deploy
echo "Deploying..."
./build/bin/shard_deploy 

# Step 4: start client
echo "Starting client..."
python ./source/py_utils/launch_remote.py --launch_part storage_client --test_index 9

sleep 5  # Give client a bit of head start

# Step 5: start controller
echo "Starting controller..."
./build/bin/shard_ctl 4 $GLOBAL_CONTROLLER_PORT_FOR_SUBSCRIBER | tee tmp/test9/log_controller.txt
