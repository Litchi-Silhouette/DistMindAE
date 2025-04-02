# PipePS

## How to Run

### Implement the model in the specific format
Please refer to import_model_reimpl_with_batching at model/resnet/resnet152/resnet152.py::19

### Build the system
You need to build the system, and add "pipeps/build/lib/python:pipeps/build/lib:pipeps" to PYTHONPATH.

* cmake for most file:
```
pipeps$ mkdir build
pipeps$ cd build
pipeps$ cmake ..
pipeps$ make
```

* setup.py for the server
```
pipeps$ cd source/server/cpp/torch
torch$ conda activate pipeswitch
torch$ python setup.py install
```

### Generate the binary file for the sotrage

The list of models in stored in `pipeps/source/deployment/model_list.txt`, which will be copied to `pipeps/build/resource/model_list.txt` when doing cmake.

example:

```
pipeps$ python build/bin/generate_file.py build/resource/model_list.txt build/kv.bin
```

### Start the storage and load values
Start the metadata storage and storages.
Their addresses and ports should be added to pipeps/deployment/storage_list.txt, and the first line after the title is for the metadata storage.
Then add values to the storage from related files.

```
pipeps$ build/bin/metadata_storage 7777
```

```
pipeps$ build/bin/storage 7778
```

```
pipeps$ python build/bin/deploy_file.py build/resource/storage_list.txt build/resource/model_distribution_list.txt kv.bin
```

### Start the load balancer, caches and servers
```
pipeps $ build/bin/load_balancer basic [AddrForClient] [PortForClient] [AddrForServer] [PortForServer] [AddrForCache] [PortForCache] [MetadataStorageAddr] [MetadataStoragePort] 
```

```
pipeps $ build/bin/cache [AddrForServer] [PortForServer] [MetadataStorageAddr] [MetadataStoragePort] [LBAddr] [LBPort] [ShmName] [ShmSize] [ShmBlockSize]
```

```
pipeps $ python build/bin/server.py [AddrForClient] [PortForClient] [CacheAddr] [CachePort] [LBAddr] [LBPort]
```

### Start the client
client_one.py is the simplest client, which sends the next request after finishing the last request. Other more complicated clients are in implementation.

```
pipeps$ python build/bin/client_one.py build/resource/request_list.txt [LBAddr] [LBPort]
```