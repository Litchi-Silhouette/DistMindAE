#ifndef BALANCE_LB_CLIENT_AGENT_H
#define BALANCE_LB_CLIENT_AGENT_H

#include <unistd.h>

#include <string>
#include <memory>
#include <mutex>

#include "tcp.h"

uint64_t client_generate_id();

struct Message {
    uint64_t id;
    std::string model_name;
    std::shared_ptr<char> data_ptr;
    size_t data_size;
};

class ClientAgent {
public:
    ClientAgent(std::shared_ptr<TcpAgent> agent);
    ~ClientAgent();

    std::shared_ptr<Message> recvRequest();
    void sendResponse(std::shared_ptr<Message> response);

private:
    std::shared_ptr<TcpAgent> _agent;
};

#endif