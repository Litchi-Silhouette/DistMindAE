import sys

import torch
import torch.nn.functional as F

from model.index import get_model_module
resnet152 = get_model_module('resnet152')
import_model_reimpl = resnet152.import_model_reimpl()
import_data = resnet152.import_data

def main():
    func_list  = import_model_reimpl()

    input_batch = import_data(1)[0]

    input_batch = input_batch.to('cuda')
    for _, _, param, _, _, _ in func_list:
        for key in param:
            param[key] = param[key].to('cuda')

    intermediate = [input_batch]
    with torch.no_grad():
        for layer_name, input_index, param, hyperparam, _, _ in func_list:
            try:
                func = getattr(F, layer_name)
            except:
                func = getattr(torch, layer_name)
            input = [intermediate[i] for i in input_index]
            output = func(*input, **param, **hyperparam)
            intermediate.append(output)

    print (intermediate[-1][0].sum().item())

if __name__ == "__main__":
    main()