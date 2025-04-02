import sys
import time
import struct
import socket
import pickle

import torch
import torch.nn.functional as F

from model.index import get_model_module
resnet152 = get_model_module('resnet152')

SERVER_ADDRESS = '10.161.159.36'
SERVER_PORT = 12345

def warmup():
    model = resnet152.import_model()
    data, _ = resnet152.import_data(1)

    model = model.cuda()
    data = data.cuda()
    with torch.no_grad():
        output = model(data)
        print (output[0].sum().item())

def main():
    # Warmup CUDA
    warmup()

    # Allocate GPU memory
    # print (torch.randn(128, 1024, 1024, device='cuda').sum().item())
    print (torch.cuda.memory_cached(), torch.cuda.memory_allocated())

    # Connect to the server
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((SERVER_ADDRESS, SERVER_PORT))


    # Import data
    data, _ = resnet152.import_data(8)
    data = data.cuda()
    print (torch.cuda.memory_cached(), torch.cuda.memory_allocated())

    # Request model
    padded_model_name = '%32s' % 'resnet152'
    padded_model_name_b = padded_model_name.encode()
    conn.send(padded_model_name_b)

    # Get parameters
    param_length_b = conn.recv(4, socket.MSG_WAITALL)
    param_length = struct.unpack('I', param_length_b)[0]
    param_b = conn.recv(param_length, socket.MSG_WAITALL)
    param_list = pickle.loads(param_b)
    for param in param_list:
        for key in param:
            param[key] = param[key].to('cuda')
    print (torch.cuda.memory_cached(), torch.cuda.memory_allocated())
    time.sleep(1)

    # Get model
    time_1 = time.time()
    conn.send(b'RECV')
    print ('Request', time.time())
    model_length_b = conn.recv(4, socket.MSG_WAITALL)
    model_length = struct.unpack('I', model_length_b)[0]
    model_b = conn.recv(model_length, socket.MSG_WAITALL)
    print ('Replied', time.time())
    func_info_list = pickle.loads(model_b)
    print ('Deserialize', time.time())

    # Compute
    intermediate = [data]
    with torch.no_grad():
        for func_info, param in zip(func_info_list, param_list):
            layer_name, input_index, hyperparam = func_info
            try:
                func = getattr(F, layer_name)
            except:
                func = getattr(torch, layer_name)
            input = [intermediate[i] for i in input_index]
            output = func(*input, **param, **hyperparam)
            intermediate.append(output)
    print (intermediate[-1].sum().item())
    print ('Complete', time.time())
    time_2 = time.time()
    latency = (time_2 - time_1) * 1000
    print ('Latency: %f ms' % latency)

    conn.close()

if __name__ == "__main__":
    main()