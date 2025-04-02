import sys
import struct
import queue
import threading
import time
# import socket

import numpy as np
import torch

from model.index import get_model_module
from source.py_utils.tcp import TcpClient

def prepare_request_binary(request_model, request_size):
    model_module = get_model_module(request_model)
    images, targets = model_module.import_data(request_size)
    
    images_b = images.numpy().tobytes()
    targets_b = targets.numpy().tobytes()

    if 'train' in request_model:
        data_b = struct.pack('I', len(images_b)) + images_b + targets_b
    else:
        data_b = images_b
    
    return data_b

def main():
    lb_address = sys.argv[1]
    lb_port = int(sys.argv[2])
    
    request_model = 'resnet152-train'
    request_size = 96
    while True:
        data_b = prepare_request_binary(request_model, request_size)
        
        time_1 = time.time()
        # Connect to LB
        lb = TcpClient(lb_address, lb_port)
        # send model_name and data
        model_name_b = request_model.encode()
        lb.tcpSendWithLength(model_name_b)
        lb.tcpSendWithLength(data_b)
        # Get response
        output_b = lb.tcpRecvWithLength()
        time_2 = time.time()

        latency = (time_2 - time_1) * 1000
        output = torch.from_numpy(np.frombuffer(output_b, dtype=np.float32))
        print (request_model, "Latency: %f ms" % latency, output[0].sum().item())

if __name__ == "__main__":
    main()