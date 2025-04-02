import sys
import struct
import time

import numpy as np
import torch

from source.py_utils.tcp import TcpClient
from model.index import get_model_module

def get_input_data(model_name):
    module = get_model_module(model_name)
    data, _ = module.import_data(8)
    return data

def main():
    lb_addr = sys.argv[1]
    lb_port = int(sys.argv[2])

    client = TcpClient(lb_addr, lb_port)

    model_name = 'resnet152'
    data = get_input_data(model_name)
    client.tcpSendWithLength(model_name.encode())
    client.tcpSendWithLength(data.numpy().tobytes())
    ret_b = client.tcpRecvWithLength()
    ret = torch.from_numpy(np.frombuffer(ret_b, dtype=np.float32))
    print (ret.sum())

if __name__ == "__main__":
    main()