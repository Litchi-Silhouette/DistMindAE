source settings/config.sh

NUM_MODELS=$GLOBAL_NUM_MODELS
DISTRIBUTION_RANK=1

python build/bin/generate_model_list.py settings/model_list_seed.txt $NUM_MODELS $DISTRIBUTION_RANK build/resource/model_list.txt
echo "Generate model list"
sleep 1

python build/bin/generate_model_distribution.py settings/storage_list.txt build/resource/model_list.txt build/resource/model_distribution.txt
echo "Generate model distribution"
sleep 1

python build/bin/generate_file.py build/resource/model_list.txt build/resource/kv.bin
echo "Generate binary files for models"

echo "Complete"