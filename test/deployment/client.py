import sys
import struct
import time
import socket
import pickle

import torch

import deployment_c

from source.py_utils.tcp import TcpClient

KVSTORAGE_OP_READ = 0
KVSTORAGE_OP_WRITE = 1
KVSTORAGE_OP_ACK = 2

def import_model_list(filename):
    with open(filename) as f:
        _ = f.readline()
        return [line.split(',')[0].strip() for line in f.readlines()]

def read_from_metadata_storage(hostname, key):
    client = TcpClient(hostname[0], hostname[1])
    op = KVSTORAGE_OP_READ
    op_b = struct.pack('I', op)
    client.tcpSend(op_b)

    client.tcpSendWithLength(key.encode())
    ret_b = client.tcpRecvWithLength()
    return ret_b

def main():
    address = sys.argv[1]
    port = int(sys.argv[2])
    model_filename = sys.argv[3]
    shm_name = sys.argv[4]
    shm_size = int(sys.argv[5])

    deployment_c.initialize(shm_name, shm_size)

    hostname = (address, port)
    model_list = import_model_list(model_filename)
    for model_name in model_list:
        model_size_key = model_name + "-SIZE"
        model_size_b = read_from_metadata_storage(hostname, model_size_key)
        model_size = struct.unpack('Q', model_size_b)[0]
        print (model_size_key, model_size)

        model_metadata_location_key = model_name + '-METADATA' + '-LOCATION'
        model_metadata_location_b = read_from_metadata_storage(hostname, model_metadata_location_key)
        metadata_offset, metadata_size, storage_id = struct.unpack('QQQ', model_metadata_location_b)
        print (model_metadata_location_key,  metadata_offset, metadata_size, storage_id)

        store_cli_id_b = struct.pack('Q', storage_id)
        addr = socket.inet_ntoa(store_cli_id_b[:4])
        port = struct.unpack('I', store_cli_id_b[4:])[0]
        store_cli_name = 'test_deployment_client'
        deployment_c.connect(store_cli_name, addr, port)

        model_metadata_key = model_name + '-METADATA'
        print (store_cli_name)
        print (model_metadata_key)
        model_metadata_b = deployment_c.get_kv_bytes(store_cli_name, model_metadata_key, metadata_size)
        print (model_metadata_key, len(model_metadata_b))

        offset = 0

        size = 4
        model_pyinfo_length = struct.unpack('I', model_metadata_b[offset: offset + size])[0]
        offset += size
        print ('Model pyinfo length', model_pyinfo_length)
        
        size = model_pyinfo_length
        model_pyinfo_b = model_metadata_b[offset: offset + size]
        offset += size

        func_info, batch_list = pickle.loads(model_pyinfo_b)
        print (len(func_info), len(batch_list))
        for batch_ptr, batch_size in batch_list:
            print ('Batch info', batch_ptr, batch_size)
        for layer_name, _, param_info, _, _, _ in func_info:
            print (layer_name, param_info)

        
        size = 4
        num_batch = struct.unpack('I', model_metadata_b[offset: offset + size])[0]
        offset += size
        print ('Number of batches', num_batch)

        for _ in range(num_batch):
            size = 4
            batch_name_length = struct.unpack('I', model_metadata_b[offset: offset + size])[0]
            offset += size

            size = batch_name_length
            batch_name = model_metadata_b[offset: offset + size].decode()
            offset += size

            print ('\t', 'Batch', batch_name_length, batch_name)

            batch_location_key = batch_name + '-LOCATION'
            batch_location_b = read_from_metadata_storage(hostname, batch_location_key)
            for _ in range(len(batch_location_b) // 24):
                slice_offset, slice_size, storage_id = struct.unpack('QQQ', batch_location_b)
                storage_id_b = struct.pack('Q', storage_id)
                addr = socket.inet_ntoa(storage_id_b[:4])
                port = struct.unpack('I', storage_id_b[4:])[0]
                print ('\t\t', batch_location_key, addr, port, slice_offset, slice_size)
        

if __name__ == "__main__":
    main()