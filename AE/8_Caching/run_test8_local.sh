#!/bin/bash
source settings/config.sh

set -e  # Exit on error

mkdir -p tmp
rm -rf tmp/test8
mkdir -p tmp/test8

./AE/8_Caching/run_distmind_test8.sh

echo "Test 8 completed successfully."