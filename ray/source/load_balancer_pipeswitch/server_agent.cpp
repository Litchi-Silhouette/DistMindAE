#include <unistd.h>
#include <string.h>

#include <string>
#include <iostream>

#include "server_agent.h"

using namespace std;

inline string getIpFromAddr(string address) {
    return address.substr(0, address.find(":"));
}
inline int getPortFromAddr(string address) {
    return stoi(address.substr(address.find(":"), address.length()));
}

ServerAgent::ServerAgent(string address):
TcpClient(getIpFromAddr(address), getPortFromAddr(address)) {}

ServerAgent::~ServerAgent() {}

shared_ptr<Message> ServerAgent::handleRequest(shared_ptr<Message> request) {
    tcpSendString(request->model_name);
    tcpSendWithLength(request->data_ptr, request->data_size);
    shared_ptr<Message> response;
    tcpRecvWithLength(response->data_ptr, response->data_size);
    return response;
}