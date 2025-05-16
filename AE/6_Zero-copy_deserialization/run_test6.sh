#!/bin/bash
source settings/config.sh

set -e  # Exit on error

mkdir -p tmp
rm -rf tmp/test6
mkdir -p tmp/test6

python ./source/des_eval/eval.py --output tmp/test6/eval_results.txt
