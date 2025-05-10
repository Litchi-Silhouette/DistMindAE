import requests
import threading
import json
from requests.api import request
import numpy as np
import random
import argparse

import time

parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str)
parser.add_argument("--ngpus", type=int)

args = parser.parse_args()

ray_logo_bytes = requests.get(
    "https://github.com/ray-project/ray/raw/"
    "master/doc/source/images/ray_header_logo.png").content
print('get ray logo')

# node_ip = "10.0.85.164"
node_ip = args.ip
node_port = "8000"

def make_req(data, endpoint):
    # print(data)
    resp = requests.post(
        f"http://{node_ip}:{node_port}/{endpoint}/query", data=data)
    try:
        print(resp.json())
    except:
        print(resp)

n_gpus = args.ngpus

def requests_loop(gpu_id, model_choice_n, repeat):
    model_idx_range = list(range(10))
    for _ in range(model_choice_n):
        model_idx = random.choice(model_idx_range)
        for j in range(repeat):
            resp = requests.get(f"http://{node_ip}:{node_port}/gpu-{gpu_id}/inference/{model_idx}")
            try:
                print(f"gpu-{gpu_id}: {j}: {resp.jsonj()}")
            except:
                print(f"gpu-{gpu_id}: {j} : {resp}")

threads = []
for i in range(n_gpus):
    t = threading.Thread(target=requests_loop, args=(i, 3, 2))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

inference_count = {}
training_count = {}
# check inference count
for i in range(n_gpus):
    resp = requests.get(url=f"http://{node_ip}:{node_port}/gpu-{i}/inference_count")
    print(f"gpu-{i}, inf count {resp.json()['count']}")
    inference_count[i] = resp.json()['count'] 
    resp = requests.get(url=f"http://{node_ip}:{node_port}/gpu-{i}/training_batch_count")
    print(f"gpu-{i}, train count {resp.json()['count']}")
    training_count[i] = resp.json()['count']

# training 
print("start training")
resp = requests.get(url=f"http://{node_ip}:{node_port}/gpu-0/train")
print(resp)
resp = requests.get(url=f"http://{node_ip}:{node_port}/gpu-1/train")
print(resp)

time.sleep(20)
threads = []
for i in range(n_gpus):
    t = threading.Thread(target=requests_loop, args=(i, 3, 2))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

# check inference count
for i in range(n_gpus):
    resp = requests.get(url=f"http://{node_ip}:{node_port}/gpu-{i}/inference_count")
    print(f"gpu-{i}, inf count {resp.json()['count']}, diff {resp.json()['count'] - inference_count[i]}")
    resp = requests.get(url=f"http://{node_ip}:{node_port}/gpu-{i}/training_batch_count")
    print(f"gpu-{i}, train count {resp.json()['count']}, diff {resp.json()['count'] - training_count[i]}")