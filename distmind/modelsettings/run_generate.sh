source settings/config.sh

NUM_MODELS=$1
NUM_STORAGE=$2
DISTRIBUTION_RANK=1

mkdir build/resource

python build/bin/generate_model_list.py modelsettings/model_list_seed_$3.txt $NUM_MODELS $DISTRIBUTION_RANK build/resource/model_list_$3$NUM_MODELS.txt
echo "Generate model list"
sleep 1

python build/bin/generate_model_distribution.py storagesettings/storage_list_$NUM_STORAGE.txt build/resource/model_list_$3$NUM_MODELS.txt build/resource/model_distribution_$3$NUM_MODELS.txt
echo "Generate model distribution"
sleep 1

python build/bin/generate_file.py build/resource/model_list_$3$NUM_MODELS.txt build/resource/kv_$3$NUM_MODELS.bin
echo "Generate binary files for models"

echo "Complete"