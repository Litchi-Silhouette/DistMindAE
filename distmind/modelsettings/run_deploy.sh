echo "Deploy models"
echo ""

NUM_MODELS=$1

sleep 1
FI_EFA_ENABLE_SHM_TRANSFER=0 python build/bin/deploy_file.py settings/storage_list.txt build/resource/model_distribution_$2$NUM_MODELS.txt build/resource/kv_$2$NUM_MODELS.bin deploy_file 1000000000