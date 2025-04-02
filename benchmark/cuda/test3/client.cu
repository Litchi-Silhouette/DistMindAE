#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#include <iostream>
#include <string>

#include "../../../source/utils/shared_memory/shared_memory.h"
#include "../../../source/utils/tcp/tcp.h"
#include "../../../source/utils/common/time.h"

using namespace std;
using namespace balance::util;

int main(int argc, char** argv) {
    // Connect to the server
    TcpClient client(string("127.0.0.1"), 7777);
    char buffer[8];

    // Create shared memory
    string name("test-pin");
    size_t size = 256 * 1024 * 1024;
    SharedMemory shm(name, size, true);
    memset(shm.getPointer(), 0, shm.getSize());
    int *data = (int*)shm.getPointer();
    int n = shm.getSize() / sizeof(int);

    // Create cuda stream
    cudaStream_t stream1;
    cudaStreamCreate(&stream1);
    int *d_data;
    cudaMalloc(&d_data, shm.getSize()); 

    // Signal Reader
    memset(buffer, 0, 8);
    memcpy(buffer, "ABCD", 4);
    client.tcpSend(buffer, 4);

    // Get signal
    memset(buffer, 0, 8);
    client.tcpRecv(buffer, 4);
    cout << buffer << endl;

    // Read something
    double time_1, time_2, latency;
    cudaError_t e;

	time_1 = time_now();
	e = cudaHostRegister(shm.getPointer(), shm.getSize(), cudaHostRegisterDefault);
    time_2 = time_now();
    cout << cudaGetErrorString(e) << endl;
    latency = time_2 - time_1;
    cout << "Latency for pinning memory: " << fixed << latency << endl;
    
    time_1 = time_now();
    e = cudaMemcpyAsync(d_data, data, shm.getSize(), cudaMemcpyHostToDevice, stream1);
    time_2 = time_now();
    cout << cudaGetErrorString(e) << endl;
    latency = time_2 - time_1;
    cout << "Latency for transmission: " << fixed << latency << endl;

    return 0;
}