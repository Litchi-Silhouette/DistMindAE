import sys

import torch

from model.index import get_model_module
resnet152 = get_model_module('resnet152')
import_model = resnet152.import_model()
import_data = resnet152.import_data

def main():
    model = import_model()
    input_batch = import_data(1)[0]

    input_batch = input_batch.to('cuda')
    model.to('cuda')

    def print_intermediate(mod, input, output):
        print (mod.fullname, input[0].sum().item(), output.sum().item())
    # for mod in model.children():
    #     mod.register_forward_hook(print_intermediate)

    with torch.no_grad():
        output = model(input_batch)
    print(output[0].sum().item())

if __name__ == "__main__":
    main()