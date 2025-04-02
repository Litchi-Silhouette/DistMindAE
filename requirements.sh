# apt-get
sudo apt-get install wget unzip

# LibTorch
if [ $USE_CUDA = 1 ]
then
    wget -O libtorch.zip https://download.pytorch.org/libtorch/cu101/libtorch-cxx11-abi-shared-with-deps-1.3.0.zip
else
    wget -O libtorch.zip https://download.pytorch.org/libtorch/cpu/libtorch-shared-with-deps-1.4.0%2Bcpu.zip
fi
unzip libtorch.zip
rm libtorch.zip