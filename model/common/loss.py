import torch

def create_criterion(loss_name):
    if loss_name == "cross_entropy":
        return torch.nn.CrossEntropyLoss()
    else:
        return None