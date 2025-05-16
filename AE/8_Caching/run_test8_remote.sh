#!/bin/bash
source settings/config.sh

set -e  # Exit on error

mkdir -p tmp
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp --test_index 8
rm -rf tmp/test8
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp/test8 --test_index 8 --stop
mkdir -p tmp/test8
python ./source/py_utils/launch_remote.py --launch_part create_dir  --log_dir tmp/test8 --test_index 8


./AE/8_Caching/run_distmind_test8_remote.sh

echo "Test 8 completed successfully."