#include <unistd.h>

#include <iostream>
#include <string>
#include <mutex>

#include "tcp.h"
#include "client_agent.h"

using namespace std;

uint64_t _client_id_generator = 0;
mutex _lock;

uint64_t client_generate_id() {
    const lock_guard<mutex> guard(_lock);
    return ++_client_id_generator;
}

ClientAgent::ClientAgent(shared_ptr<TcpAgent> agent): _agent(agent) {}

ClientAgent::~ClientAgent() {}

shared_ptr<Message> ClientAgent::recvRequest() {
    shared_ptr<Message> request(new Message());
    if (ERRNO_SUCCESS != _agent->tcpRecvString(request->model_name))
        return nullptr;
    if (ERRNO_SUCCESS != _agent->tcpRecvWithLength(request->data_ptr, request->data_size))
        return nullptr;
    return request;
}

void ClientAgent::sendResponse(shared_ptr<Message> response) {
    if (ERRNO_SUCCESS != _agent->tcpSendWithLength(response->data_ptr, response->data_size))
        cout << "Reply Error" << endl;
}