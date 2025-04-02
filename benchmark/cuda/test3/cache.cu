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
    // Open shared memory
    string name("test-pin");
    size_t size = 256 * 1024 * 1024;
    SharedMemory shm(name, size, true);
    memset(shm.getPointer(), 0, shm.getSize());
    int *data = (int*)shm.getPointer();
    int n = shm.getSize() / sizeof(int);
    sleep(1);

    // Write something
    for (int i = 0; i < n; ++i)
        data[i] = i;

    // Pin memory
    double time_1, time_2, latency;
    cudaError_t e;
    time_1 = time_now();
	e = cudaHostRegister(shm.getPointer(), shm.getSize(), cudaHostRegisterDefault);
    time_2 = time_now();
    cout << cudaGetErrorString(e) << endl;
    latency = time_2 - time_1;
    cout << "Latency for pinning memory: " << fixed << latency << endl;

    // Accept connection
    TcpServer server(string("127.0.0.1"), 7777);
    TcpAgent* agent = server.tcpAccept();
    char buffer[8];

    // Get signal
    memset(buffer, 0, 8);
    agent->tcpRecv(buffer, 4);
    cout << buffer << endl;

    // Signal writer
    memset(buffer, 0, 8);
    memcpy(buffer, "WXYZ", 4);
    agent->tcpSend(buffer, 4);

    // Wait for completion
    sleep(1);

    delete agent;

    return 0;
}