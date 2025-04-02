#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#include <string>
#include <iostream>

#include "../../source/utils/tcp/tcp.h"

using namespace std;
using namespace balance::util;

int main(int argc, char** argv) {
    if (argc < 3) {
        cout << "Arguments Error" << endl;
        return 1;
    }
    string address(argv[1]);
    int port = atoi(argv[2]);

    TcpServer server(address, port);
    TcpAgent agent = server.tcpAccept();
    
    char *buffer = (char*)malloc(8);
    memset(buffer, 0, 8);

    for (int i = 0; i < 100; ++i) {
        agent.tcpRecv(buffer, sizeof(int));
        *(int*)buffer = *(int*)buffer + 1;
        agent.tcpSend(buffer, sizeof(int));
    }

    return 0;
}