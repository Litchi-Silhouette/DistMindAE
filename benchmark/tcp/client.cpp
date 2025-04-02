#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#include <string>
#include <iostream>

#include "../../source/utils/tcp/tcp.h"
#include "../../source/utils/common/time.h"

using namespace std;
using namespace balance::util;

int main(int argc, char** argv) {
    if (argc < 3) {
        cout << "Arguments Error" << endl;
        return 1;
    }
    string address(argv[1]);
    int port = atoi(argv[2]);

    TcpClient client(address, port);

    char *buffer = (char*)malloc(8);
    memset(buffer, 0, 8);

    double max_latency = 0.0;
    for (int i = 0; i < 100; ++i) {
        *(int*)buffer = i * 2;
        double time_1 = time_now();
        client.tcpSend(buffer, sizeof(int));
        client.tcpRecv(buffer, sizeof(int));
        double time_2 = time_now();
        double latency = time_2 - time_1;
        if (*(int*)buffer != i * 2 + 1)
            cout << "Message Error: " << i << endl;
        else
            cout << "Correct with latency: " << fixed << latency << endl;
        if (latency > max_latency)
            max_latency = latency;
    }
    cout << "Max latency: " << fixed << max_latency << endl;

    return 0;
}