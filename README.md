# DistMindAE

## description

+ ray: ray 相关
+ distmind: in gpu/mps/dismind 相关

## preparing

1. aws efa 
2. cuda-11.7 / PyTorch 1.13.1 / python3.9 / cuDNN: 9.6.0
3. pip install transformers==4.4.0
4. pip install -U "ray[all]"
5. pybind11: （distmind）git submodule update --init xx最新的！
6. spdlog    sudo apt install libspdlog-dev
7. libtorch : https://download.pytorch.org/libtorch/cu117/libtorch-shared-with-deps-1.13.1%2Bcu117.zip  pre-c11 ABI  解压到distmind

## distmind

1. 修改config
2. ./scripts/run_generate.sh
3. ./scripts/run_storage.sh
4. ./scripts/run_metadata.sh
5. ./scripts/run_deploy.sh
6. ./scripts/run_server.sh
7. ./scripts/run_controller.sh
8. run client