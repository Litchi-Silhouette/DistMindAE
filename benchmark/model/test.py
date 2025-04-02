import sys
import time
import pickle

import torch
import torch.nn.functional as F

from model.common.util import extract_func_info, evaluate_model_forward

from model.index import get_model_module
resnet152 = get_model_module('resnet152')
import_model_reimpl = resnet152.import_model_reimpl()
import_data = resnet152.import_data

def main():
    func_list  = import_model_reimpl()

    func_info_list = extract_func_info(func_list)
    param_list = [param for _, _, param, _, _, _ in func_list]

    time_1 = time.time()
    func_info_bytes = pickle.dumps(func_info_list)
    time_2 = time.time()
    latency = (time_2 - time_1) * 1000
    print ('Latency for serializing info:', latency)

    time_1 = time.time()
    func_info_back = pickle.loads(func_info_bytes)
    time_2 = time.time()
    latency = (time_2 - time_1) * 1000
    print ('Latency for deserializing info:', latency)

    input_batch = import_data(1)[0]

    input_batch = input_batch.to('cuda')
    for param in param_list:
        for key in param:
            param[key] = param[key].to('cuda')

    with torch.no_grad():
        output = evaluate_model_forward(input_batch, func_info_back, param_list)
    print (output[0].sum().item())

if __name__ == "__main__":
    main()