echo "Deploy models"
echo ""

NUM_MODELS=$1
NUM_STORAGE=$2

sleep 1
FI_EFA_ENABLE_SHM_TRANSFER=0 python build/bin/deploy_file.py storagesettings/storage_list_$NUM_STORAGE.txt build/resource/model_distribution_$3$NUM_MODELS.txt build/resource/kv_$3$NUM_MODELS.bin deploy_file 1000000000