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
    SharedMemory shm(name, size);
    memset(shm.getPointer(), 0, shm.getSize());
    int *data = (int*)shm.getPointer();
    int n = shm.getSize() / sizeof(int);

    TcpClient client(string("127.0.0.1"), 7777);
    char buffer[8];


    // Write something
    for (int i = 0; i < n; ++i)
        data[i] = i;

    // Signal Reader
    memset(buffer, 0, 8);
    memcpy(buffer, "ABCD", 4);
    client.tcpSend(buffer, 4);

    // Get signal
    memset(buffer, 0, 8);
    client.tcpRecv(buffer, 4);
    cout << buffer << endl;

    // Read something
    for (int i = 0; i < n; ++i)
        if (data[i] != i * i)
            cout << "Error: " << i << ", " << data[i] << endl;

    return 0;
}