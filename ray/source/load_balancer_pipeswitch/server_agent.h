#ifndef BALANCE_LB_SERVER_AGENT_H
#define BALANCE_LB_SERVER_AGENT_H

#include <unistd.h>

#include <string>
#include <memory>
#include <mutex>
#include <unordered_map>

#include "client_agent.h"

class ServerAgent: public TcpClient {
public:
    ServerAgent(std::string address);
    ~ServerAgent();

    std::shared_ptr<Message> handleRequest(std::shared_ptr<Message> request);

private:
    std::mutex _lock;
};

#endif