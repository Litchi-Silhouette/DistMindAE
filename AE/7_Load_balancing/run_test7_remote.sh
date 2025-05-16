#!/bin/bash
source settings/config.sh

set -e  # Exit on error

mkdir -p tmp
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp --test_index 7
rm -rf tmp/test7
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp/test7 --test_index 7 --stop
mkdir -p tmp/test7
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp/test7 --test_index 7

# in gpu
mkdir -p tmp/test2
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp/test2 --test_index 7
mkdir -p tmp/test2/gpu
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmptest2/gpu --test_index 7

echo "======================================================================================"
echo "Running gpu test"
echo "======================================================================================"
    
# Run the test for this seed and size
./AE/2_End-to-end_performance/run_distmind_test2_remote.sh 1 "res" "gpu"
    
# Wait a bit between runs to ensure clean shutdown
sleep 10

# Run distmind tests for each model seed with corresponding size
echo "======================================================================================"
echo "Running distmind test"
echo "======================================================================================"
    
# Run the test for this seed and size
./AE/7_Load_balancing/run_distmind_test7_remote.sh $GLOBAL_NUM_MODELS "res" "load_balancer"
    
# Wait a bit between runs to ensure clean shutdown
sleep 10

# lfu

# Run lfu tests for each model seed with corresponding size
echo "======================================================================================"
echo "Running lfu test"
echo "======================================================================================"
    
# Run the test for this seed and size
./AE/7_Load_balancing/run_distmind_test7_remote.sh $GLOBAL_NUM_MODELS "res" "lb_lfu"
    
# Wait a bit between runs to ensure clean shutdown
sleep 10
