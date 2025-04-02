WORK_DIR=$(shell pwd)
SOURCE_DIR=$(WORK_DIR)/source
BUILD_DIR=$(WORK_DIR)/build_server
UTILS_DIR=$(BUILD_DIR)/tmp/utils.o

CUDA_PATH=/usr/local/cuda

_GLIBCXX_USE_CXX11_ABI=0

CC=g++
NVCC=$(CUDA_PATH)/bin/nvcc
# CPPFLAGS=-std=c++11 -I$(BUILD_DIR)/include -L$(BUILD_DIR)/lib
CPPFLAGS=-std=c++11 -I$(SOURCE_DIR) -D_GLIBCXX_USE_CXX11_ABI=$(_GLIBCXX_USE_CXX11_ABI)
LIBRARY=-lpthread -lrt

all: py_utils utils client load_balancer server cache metadata_storage deployment

# build_dir:
# 	if test -f "$FILE"; then
# 		echo "$FILE exist"
# 	fi
# 	mkdir $(BUILD_DIR)
# 	# mkdir $(BUILD_DIR)/include
# 	# mkdir $(BUILD_DIR)/lib
# 	mkdir $(BUILD_DIR)/bin
# 	mkdir $(BUILD_DIR)/tmp

py_utils:
	mkdir -p $(BUILD_DIR)/py_utils
	cp $(SOURCE_DIR)/py_utils/tcp.py $(BUILD_DIR)/py_utils/

client: py_utils
	mkdir -p $(BUILD_DIR)/client
	cp $(SOURCE_DIR)/client/client.py $(BUILD_DIR)/client/
	cp $(SOURCE_DIR)/client/request_list.txt $(BUILD_DIR)/client/

utils: common tcp tcp_pattern communicator shared_memory memory_manager
	mkdir -p $(BUILD_DIR)/tmp
	# cp $(SOURCE_DIR)/utils/utils.h $(BUILD_DIR)/include/utils/
	# gcc -o $(BUILD_DIR)/tmp/utils.o $(BUILD_DIR)/tmp/tcp.o $(BUILD_DIR)/tmp/tcp_pattern.o $(BUILD_DIR)/tmp/shared_memory.o $(BUILD_DIR)/tmp/memory_manager.o
	$(CC) -o $(UTILS_DIR) $(BUILD_DIR)/tmp/tcp.o $(BUILD_DIR)/tmp/tcp_pattern.o $(BUILD_DIR)/tmp/shared_memory.o $(BUILD_DIR)/tmp/memory_manager.o -shared -fPIC $(CPPFLAGS) $(LIBRARY)

load_balancer: utils \
	$(SOURCE_DIR)/load_balancer/load_balancer.cpp \
	$(SOURCE_DIR)/load_balancer/metadata_manager.cpp \
	$(SOURCE_DIR)/load_balancer/client_agent.cpp \
	$(SOURCE_DIR)/load_balancer/cache_agent.cpp \
	$(SOURCE_DIR)/load_balancer/server_agent.cpp \
	$(SOURCE_DIR)/load_balancer/strategy/strategy.cpp \
	$(SOURCE_DIR)/load_balancer/strategy/basic_strategy.cpp
	mkdir -p $(BUILD_DIR)/bin
	$(CC) -o $(BUILD_DIR)/bin/load_balancer.out $(filter %.cpp,$^) $(UTILS_DIR) $(CPPFLAGS) $(LIBRARY)

server: utils
	mkdir -p $(BUILD_DIR)/server
	export SOURCE_DIR=$(SOURCE_DIR) && \
	export UTILS_DIR=$(UTILS_DIR) && \
	cd $(SOURCE_DIR)/server/cpp_extension/torch && \
	python setup.py install
	cp $(SOURCE_DIR)/server/server.py $(BUILD_DIR)/server/

cache: utils \
	$(SOURCE_DIR)/cache/cache.cpp \
	$(SOURCE_DIR)/cache/lb_agent.cpp \
	$(SOURCE_DIR)/cache/model_manager.cpp \
	$(SOURCE_DIR)/cache/storage_agent.cpp
	mkdir -p $(BUILD_DIR)/bin
	$(CC) -o $(BUILD_DIR)/bin/cache.out $(filter %.cpp,$^) $(UTILS_DIR) $(CPPFLAGS) $(LIBRARY)

metadata_storage: utils $(SOURCE_DIR)/metadata_storage/metadata_storage.cpp
	mkdir -p $(BUILD_DIR)/bin
	$(CC) -o $(BUILD_DIR)/bin/metadata_storage.out $(filter %.cpp,$^) $(UTILS_DIR) $(CPPFLAGS) $(LIBRARY)

deployment: py_utils
	mkdir -p $(BUILD_DIR)/deployment
	cp $(SOURCE_DIR)/deployment/deployment.py $(BUILD_DIR)/deployment/
	cp $(SOURCE_DIR)/deployment/storage_list.txt $(BUILD_DIR)/deployment/
	cp $(SOURCE_DIR)/deployment/model_list.txt $(BUILD_DIR)/deployment/

# utils_dir:
# 	# mkdir $(BUILD_DIR)/include/utils 

common:
	mkdir -p $(BUILD_DIR)/tmp
	# mkdir $(BUILD_DIR)/include/utils/common 
	# cp $(SOURCE_DIR)/utils/common/atomic.h $(BUILD_DIR)/include/utils/common
	# cp $(SOURCE_DIR)/utils/common/dispatcher.h $(BUILD_DIR)/include/utils/common
	# cp $(SOURCE_DIR)/utils/common/errno.h $(BUILD_DIR)/include/utils/common
	# cp $(SOURCE_DIR)/utils/common/global.h $(BUILD_DIR)/include/utils/common
	# cp $(SOURCE_DIR)/utils/common/pointer.h $(BUILD_DIR)/include/utils/common
	# cp $(SOURCE_DIR)/utils/common/time.h $(BUILD_DIR)/include/utils/common

tcp: common $(SOURCE_DIR)/utils/tcp/tcp.cpp
	mkdir -p $(BUILD_DIR)/tmp
	# mkdir $(BUILD_DIR)/include/utils/tcp
	# cp $(SOURCE_DIR)/utils/tcp/tcp.h $(BUILD_DIR)/include/utils/tcp
	$(CC) -o $(BUILD_DIR)/tmp/tcp.o $(filter %.cpp,$^) -c -shared -fPIC $(CPPFLAGS) $(LIBRARY)

tcp_pattern: common tcp $(SOURCE_DIR)/utils/tcp_pattern/tcp_pattern.cpp
	mkdir -p $(BUILD_DIR)/tmp
	# mkdir $(BUILD_DIR)/include/utils/tcp_pattern
	# cp $(SOURCE_DIR)/utils/tcp_pattern/tcp_pattern.h $(BUILD_DIR)/include/utils/tcp_pattern
	$(CC) -o $(BUILD_DIR)/tmp/tcp_pattern.o $(filter %.cpp,$^) -c -shared -fPIC $(CPPFLAGS) $(LIBRARY)

communicator: common
	mkdir -p $(BUILD_DIR)/tmp
	# cd $(SOURCE_DIR)/utils/communicator
	# make
	# cd $(WORK_DIR)
	# mkdir $(BUILD_DIR)/include/utils/communicator
	# cp $(SOURCE_DIR)/utils/communicator/communicator.h $(BUILD_DIR)/include/utils/communicator

shared_memory: common $(SOURCE_DIR)/utils/shared_memory/shared_memory.cpp
	mkdir -p $(BUILD_DIR)/tmp
	# mkdir $(BUILD_DIR)/include/utils/shared_memory
	# cp $(SOURCE_DIR)/utils/shared_memory/shared_memory.h $(BUILD_DIR)/include/utils/shared_memory
	$(CC) -o $(BUILD_DIR)/tmp/shared_memory.o $(filter %.cpp,$^) -c -shared -fPIC $(CPPFLAGS) $(LIBRARY)

memory_manager: common shared_memory $(SOURCE_DIR)/utils/memory_manager/memory_manager.cpp
	mkdir -p $(BUILD_DIR)/tmp
	# mkdir $(BUILD_DIR)/include/utils/memory_manager
	# cp $(SOURCE_DIR)/utils/memory_manager/memory_manager.h $(BUILD_DIR)/include/utils/memory_manager
	$(CC) -o $(BUILD_DIR)/tmp/memory_manager.o $(filter %.cpp,$^) -c -shared -fPIC $(CPPFLAGS) $(LIBRARY)

clean:
	rm -rf $(BUILD_DIR)
	cd $(SOURCE_DIR)/server/cpp_extension/torch && python setup.py clean --all