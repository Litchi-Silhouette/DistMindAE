from torchvision.models import resnet152, vgg16_bn, densenet201, inception_v3
import torch
import numpy as np
# model = torch.hub.load('huggingface/pytorch-transformers', 'model', 'bert-base-uncased')
from model.index import get_model_module

import time

def get_random_data(batch_size):
    data = torch.rand([batch_size, 3, 224, 224], dtype=torch.float)
    target = torch.randint(0, 1000, [batch_size])
    return data, target

def make_some_train(model, n=50):
    model = model.to('cuda')
    model.train()
    loss_fn = torch.nn.CrossEntropyLoss().cuda()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    for _ in range(n):
        images, target = get_random_data(64)
        images = images.to('cuda')
        target = target.to('cuda')
        output = model(images)
        loss = loss_fn(output, target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    model = model.to('cpu')
    model.eval()

def make_some_inf(model: torch.nn.Module, n=10):
    """"""
    inf_bs = 8
    if model.__class__.__name__ == "ResNet":
        module = get_model_module("resnet152")
    elif model.__class__.__name__ == "DenseNet":
        module = get_model_module("densenet201")
    elif model.__class__.__name__ == "Inception3":
        module = get_model_module("inception_v3")
    elif model.__class__.__name__ == "BertModel":
        module = get_model_module("bert_base")
    elif model.__class__.__name__ == "GPT2LMHeadModel":
        module = get_model_module("gpt2")

    for _ in range(n):
        images, target = module.import_data(inf_bs)
        images = images.to('cuda')
        target = target.to('cuda')
        output = model(images)
        time.sleep(0.005)


    torch.cuda.synchronize()



def benchmark_inf_latency_with_movement(old_model, new_model: torch.nn.Module, repeat=10, warmup=5, train_model=None):
    end2end_latency = []

    # make sure the model on cpu
    # model = model.to("cpu")
    for i in range(warmup + repeat):
        old_model = old_model.to("cuda")
        # old model do some inference
        make_some_inf(old_model)
        if train_model:
            make_some_train(train_model, n=10)

        torch.cuda.synchronize()

        start_t = time.time() * 1e3
        # move old model to CPU
        old_model = old_model.to("cpu")
        # move new model on 
        new_model = new_model.to("cuda")
        make_some_inf(new_model, n=1)
        torch.cuda.synchronize()
        end_t = time.time() * 1e3
        if i >= warmup:
            end2end_latency.append(end_t - start_t)

    print(f"{new_model.__class__.__name__} end2end latency {np.mean(end2end_latency)} ms")

def main():
    """"""
    resnet = resnet152(pretrained=True)
    desnet = densenet201(pretrained=True)
    inception = inception_v3(pretrained=True)
    bert = torch.hub.load('huggingface/pytorch-transformers', 'model', 'bert-base-uncased')
    gpt2 = torch.hub.load('huggingface/transformers', 'modelForCausalLM', 'gpt2')

    old_resnet = resnet152(pretrained=True)
    old_desnet = densenet201(pretrained=True)
    old_inception = inception_v3(pretrained=True)
    old_bert = torch.hub.load('huggingface/pytorch-transformers', 'model', 'bert-base-uncased')
    old_gpt2 = torch.hub.load('huggingface/transformers', 'modelForCausalLM', 'gpt2')

    old_models = [
        old_resnet, old_desnet, old_inception, 
        old_bert, old_gpt2
    ]

    models = [
        resnet, desnet, inception, 
        bert, gpt2
    ]

    for old_one, new_one in zip(old_models, models):
        benchmark_inf_latency_with_movement(old_one, new_one, train_model=resnet)

if __name__ == "__main__":
    main()