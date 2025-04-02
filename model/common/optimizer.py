import torch

def create_optimizer(optimizer_name, param_list, lr):
    param_set = []
    for param in param_list:
        for key, p in param:
            if key != 'running_mean' and key != 'running_var':
                p.requires_grad = True
                param_set.append(p)

    if optimizer_name == "sgd":
        return torch.optim.SGD(param_set, lr)
    else:
        return None