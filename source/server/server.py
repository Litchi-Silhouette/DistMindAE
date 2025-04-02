import sys
import time
import socket
import struct
import pickle
import statistics

import numpy as np
import torch 

from source.py_utils.tcp import TcpServer
import server_torch_c as balance
from model.common.util import infer_model, train_model

MODEL_BUFFER_SIZE = 1 * 1024 * 1024 * 1024

cached_info = {}
current_model = ''
update_model = True

def initializeServer():
    if len(sys.argv) < 7:
        print ('Argument Error')
        print ('program [AddrForClient] [PortForClient] [CacheAddr] [CachePort] [LBAddr] [LBPort]')
        sys.exit(1)
    address_for_client = sys.argv[1]
    port_for_client = int(sys.argv[2])
    cache_address = sys.argv[3]
    cache_port = int(sys.argv[4])
    lb_address = sys.argv[5]
    lb_port = int(sys.argv[6])

    # Initialize C++ extensions
    balance.init_server(
        address_for_client, port_for_client, 
        cache_address, cache_port, 
        lb_address, lb_port
    )

    cuda_stream = torch.cuda.Stream()
    with torch.cuda.stream(cuda_stream):
        t = torch.randn(MODEL_BUFFER_SIZE // 4, dtype=torch.float32, device='cuda')
        print ('Warmup CUDA', t.data_ptr(), t.shape)
    print ('GPU usage', torch.cuda.memory_allocated(), torch.cuda.memory_cached())

    return cuda_stream

def prepare_model(cuda_stream, func_info, batch_info):
    param_list = []
    def hook_for_parameter(input):
        global update_model
        if update_model:
            _ = balance.check_param_completion()
        print ('\tBatch in Python', time.time())
    with torch.cuda.stream(cuda_stream):
        for i in range(len(batch_info) - 1):
            batch_start = None
            batch_byte_size = batch_info[i + 1][1]
            start_layer = batch_info[i][0]
            end_layer = batch_info[i + 1][0]
            _, _, _, _, forward_pre_hooks, _ = func_info[start_layer]
            if batch_byte_size > 0 and len(forward_pre_hooks) == 0:
                forward_pre_hooks.append(hook_for_parameter)
            for _, _, param_info, _, _, _ in func_info[start_layer: end_layer]:
                param = []
                for key, p_shape, p_dtype in param_info:
                    p = torch.empty(p_shape, dtype=p_dtype, device='cuda')
                    param.append((key, p))
                    if batch_start is None:
                        batch_start = p
                param_list.append(param)
            if batch_byte_size > 0:
                balance.register_param_gpu_memory(batch_start, batch_byte_size)
    return param_list

def main():
    cuda_stream = initializeServer()

    global update_model
    global current_model
    shape = None
    func_info = None
    batch_info = None
    param_list = None
    latency_list = []
    latency_0_list = []
    while True:
        print ('GPU usage', torch.cuda.memory_allocated(), torch.cuda.memory_cached())

        # Send model name to the cache
        model_name = balance.get_task()
        start_time_0 = time.time()
        print ("Get model name:", model_name, start_time_0)

        # Decide whether to clear the GPU
        update_model = (model_name != current_model)
        if update_model:
            current_model = model_name
            del param_list
            print ('\tClear status', time.time())
        
            # Get metadata of the model from cache
            if model_name not in cached_info:
                metadata_b = balance.get_model_info()
                cached_info[model_name] = pickle.loads(metadata_b)
            shape, func_info, batch_info = cached_info[model_name]
            print ('\tGet model info', time.time())

        # Recv data
        data_b = balance.get_data()
        # Parse data
        input_batch = torch.from_numpy(np.frombuffer(data_b, dtype=shape[0][0])).reshape(-1, *(shape[0][1]))
        input_batch = input_batch.cuda(non_blocking=True)
        print ('\tPrepare data', time.time())

        start_time = time.time()
        print ('Start', start_time)
        if update_model:
            # Prepare the model and add hooks
            param_list = prepare_model(cuda_stream, func_info, batch_info)
            print ('\tPrepare model', time.time())
        
        # Compute
        output = infer_model(input_batch, func_info, param_list)        
        
        # Copy parameters back
        balance.copyback(('train' in model_name))
        
        # Send result to the LB
        output_b = output.detach().cpu().numpy().tobytes()
        balance.complete_task(model_name, output_b, len(output_b))
        end_time = time.time()
        print ('End', end_time)
        latency = (end_time - start_time) * 1000
        latency_list.append(latency)
        print ('Computation Latency: %f ms' % latency)
        latency_0 = (end_time - start_time_0) * 1000
        latency_0_list.append(latency_0)
        print ('      Total Latency: %f ms' % latency_0)
        print ()
        if len(latency_list) % 100 == 1:
            print ('Average Computation Latency: %f ms' % statistics.mean(latency_list[-1000:]))
            print ('Average       Total Latency: %f ms' % statistics.mean(latency_0_list[-1000:]))
            print ()
        
        # Clear status
        del output
        del input_batch

if __name__ == "__main__":
    main()