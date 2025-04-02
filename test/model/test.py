import sys
import time
import pickle

import torch

from model.index import model_map, get_model_module
from model.common.util import extract_func_info, evaluate_model_forward

def main():
    if len(sys.argv) < 2:
        print ('Argument Error: program [model_name]')
        sys.exit(1)
    model_name = sys.argv[1]

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    model_module = get_model_module(model_name)
    if model_module is None:
        print ('Not support model: %s' % model_name)
        print ('Supported models:')
        for key in model_map:
            print ('\t%s' % key)
        sys.exit(1)

    print ('Model name: %s' % model_module.MODEL_NAME)

    data, _ = model_module.import_data(8)
    func_list = model_module.import_model_reimpl(device=device)
    func_info, param_list = extract_func_info(func_list)

    time_1 = time.time()
    model_b = pickle.dumps(func_info)
    time_2 = time.time()
    model_back = pickle.loads(model_b)
    time_3 = time.time()
    latency_serialize = (time_2 - time_1) * 1000
    latency_deserialize = (time_3 - time_2) * 1000
    print ('Serialize time: %f ms' % latency_serialize)
    print ('Deserialize time: %f ms' % latency_deserialize)
    print ()

    data = data.to(device)
    for param in param_list:
        for _, p in param.items():
            p.data = p.to(device)

    output = evaluate_model_forward(data, func_info, param_list)
    print ('Result:', output[0].sum().item())

if __name__ == "__main__":
    main()