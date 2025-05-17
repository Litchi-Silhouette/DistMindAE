#!/bin/bash
source settings/config.sh

set -e  # Exit on error

mkdir -p tmp
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp --test_index 5
rm -rf tmp/test5
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp/test5 --test_index 5 --stop
mkdir -p tmp/test5
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp/test5 --test_index 5

MODEL_SEEDS=("res" "inc" "den" "bert" "gpt" )
REMOTE_SIZES=(128 128 128 64 64)

BATCH_SIZES=(1 1024000 2048000 32768000 131072000 262144000 10737418240)
CACHE_BLOCK_SIZES=(81920 1024000 2048000 4096000 4096000 4096000 4096000)

# in gpu
mkdir -p tmp/test1
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp/test1 --test_index 5
mkdir -p tmp/test1/gpu
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp/test1/gpu --test_index 5

# Run gpu tests for each model seed with corresponding size
echo "Running gpu tests for different model seeds..."
for i in "${!MODEL_SEEDS[@]}"; do
    SEED=${MODEL_SEEDS[$i]}
    SIZE=1
    
    echo "======================================================================================"
    echo "Running gpu test for seed: $SEED with size: $SIZE"
    echo "======================================================================================"
    
    # Run the test for this seed and size
    # ./AE/1_Meeting_latency_SLOs/run_distmind_test1_remote.sh $SIZE $SEED "gpu"
    
    # Wait a bit between runs to ensure clean shutdown
    # sleep 10
done

# distmind

# Run distmind tests for each model seed with corresponding size
echo "Running distmind tests for different model seeds..."
for j in "${!BATCH_SIZES[@]}"; do
    BATCH_SIZE=${BATCH_SIZES[$j]}
    CACHE_BLOCK_SIZE=${CACHE_BLOCK_SIZES[$j]}
    
    for i in "${!MODEL_SEEDS[@]}"; do
        SEED=${MODEL_SEEDS[$i]}
        SIZE=${REMOTE_SIZES[$i]}
    
        echo "======================================================================================"
        echo "Running distmind test for seed: $SEED with size: $SIZE batch size: $BATCH_SIZE"
        echo "======================================================================================"
        
        # Run the test for this seed and size
        ./AE/5_Three-stage_pipeline/run_distmind_test5_remote.sh $SIZE $SEED $BATCH_SIZE $CACHE_BLOCK_SIZE
        
        # Wait a bit between runs to ensure clean shutdown
        sleep 10
    done
done

python ./source/py_utils/launch_remote.py --launch_part get_output --log_dir tmp/test5 --test_index 5 --first
echo "Getting output from remote machines completed successfully."