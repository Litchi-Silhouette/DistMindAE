#!/bin/bash
source settings/config.sh

set -e  # Exit on error

mkdir -p tmp
rm -rf tmp/test7
mkdir -p tmp/test7

# in gpu
mkdir -p tmp/test2
mkdir -p tmp/test2/gpu

echo "======================================================================================"
echo "Running gpu test"
echo "======================================================================================"
    
# Run the test for this seed and size
./AE/2_End-to-end_performance/run_distmind_test2.sh 1 "res" "gpu"
    
# Wait a bit between runs to ensure clean shutdown
sleep 10

# Run distmind tests for each model seed with corresponding size
echo "======================================================================================"
echo "Running distmind test"
echo "======================================================================================"
    
# Run the test for this seed and size
./AE/7_Load_balancing/run_distmind_test7.sh $GLOBAL_NUM_MODELS "res" "load_balancer"
    
# Wait a bit between runs to ensure clean shutdown
sleep 10

# lfu

# Run lfu tests for each model seed with corresponding size
echo "======================================================================================"
echo "Running lfu test"
echo "======================================================================================"
    
# Run the test for this seed and size
./AE/7_Load_balancing/run_distmind_test7.sh $GLOBAL_NUM_MODELS "res" "lb_lfu"
    
# Wait a bit between runs to ensure clean shutdown
sleep 10
