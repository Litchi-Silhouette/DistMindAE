import sys
import time

import torch

import deployment_c

def main():
    storage_address = sys.argv[1]
    storage_port = int(sys.argv[2])
    shm_name = sys.argv[3]
    shm_size = int(sys.argv[4])

    deployment_c.initialize(shm_name, shm_size)
    deployment_c.connect('store_cli', storage_address, storage_port)

    data = torch.randn(20, 1024, 1024)
    print ('Data before put:', data.sum())
    deployment_c.put_kv_tensor('store_cli', 'test-slice', data)
    print ('Data after put:', data.sum())
    time.sleep(1)

    data_back = torch.zeros(20, 1024, 1024)
    print ('Data (back) before get:', data_back.sum())
    deployment_c.get_kv_tensor('store_cli', 'test-slice', data_back)
    print ('Data (back) after get:', data_back.sum())



if __name__ == "__main__":
    main()