import sys
import time
import struct
import socket
import pickle

import torch

from model.index import get_model_module
resnet152 = get_model_module('resnet152')

SERVER_ADDRESS = '0.0.0.0'
SERVER_PORT = 12345

def main():
    # Listen client
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((SERVER_ADDRESS, SERVER_PORT))
    s.listen(1)
    conn, _ = s.accept()

    # Import model
    func_list  = resnet152.import_model_reimpl()
    model = [(layer_name, input_index, hyperparam) for layer_name, input_index, param, hyperparam in func_list]
    param_list = [param for layer_name, input_index, param, hyperparam in func_list]

    # Listen request
    padded_model_name_b = conn.recv(32, socket.MSG_WAITALL)
    padded_model_name = padded_model_name_b.decode()
    model_name = padded_model_name.strip()

    # Reply parameters
    param_b = pickle.dumps(param_list)
    param_length = len(param_b)
    param_length_b = struct.pack('I', param_length)
    conn.send(param_length_b)
    conn.send(param_b)

    # Reply model
    conn.recv(4, socket.MSG_WAITALL)
    print ('Requested', time.time())
    model_b = pickle.dumps(model)
    model_length = len(model_b)
    model_length_b = struct.pack('I', model_length)
    conn.send(model_length_b)
    conn.send(model_b)
    print ('Replied', time.time())

    # Wait for termination
    time.sleep(10)
    conn.close()
    s.close()

if __name__ == "__main__":
    main()