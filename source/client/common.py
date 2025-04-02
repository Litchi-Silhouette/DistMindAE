import struct

from model.index import get_model_module

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

def import_request_list(filename):
    model_input = {}
    request_list = []
    with open(filename) as f:
        f.readline() # Title
        for line in f.readlines():
            parts = line.split(',')
            request_id = len(request_list)
            request_model = parts[0].strip()
            request_size = int(parts[1].strip())
            request_interval = float(parts[2].strip())
            request_list.append((request_id, request_model, request_size, request_interval))
            if (request_model, request_size) not in model_input:
                model_input[(request_model, request_size)] = prepare_request_binary(request_model, request_size)
    return request_list, model_input