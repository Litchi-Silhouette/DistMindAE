#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#include <iostream>
#include <string>

#include "../../source/utils/shared_memory/shared_memory.h"
#include "../../source/utils/tcp/tcp.h"

using namespace std;
using namespace balance::util;

int main(int argc, char** argv) {
    if (argc < 3) {
        cout << "Arguments Error" << endl;
        return 1;
    }
    string name(argv[1]);
    size_t size = atol(argv[2]);
    SharedMemory shm(name, size, true);
    memset(shm.getPointer(), 0, shm.getSize());
    int *data = (int*)shm.getPointer();
    int n = shm.getSize() / sizeof(int);

    TcpServer server(string("127.0.0.1"), 7777);
    TcpAgent agent = server.tcpAccept();
    char buffer[8];

    // Get signal
    memset(buffer, 0, 8);
    agent.tcpRecv(buffer, 4);
    cout << buffer << endl;

    // Read something
    for (int i = 0; i < n; ++i)
        if (data[i] != i)
            cout << "Error: " << i << ", " << data[i] << endl;
    
    // Write something
    for (int i = 0; i < n; ++i)
        data[i] = data[i] * data[i];

    // Signal writer
    memset(buffer, 0, 8);
    memcpy(buffer, "WXYZ", 4);
    agent.tcpSend(buffer, 4);

    return 0;
}