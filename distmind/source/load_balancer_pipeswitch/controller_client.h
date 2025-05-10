#ifndef BALANCE_LB_CONTROLLER_CLIENT_H
#define BALANCE_LB_CONTROLLER_CLIENT_H

#include <unistd.h>

#include <string>
#include <memory>
#include <vector>

#include "tcp.h"

struct ControllerUpdateNotification {
    std::string address;
    std::string model_name;
};

class ControllerClient {
public:
    ControllerClient(std::string addr, int port);
    ~ControllerClient();
    ControllerUpdateNotification getNotification();
    const std::vector<std::pair<std::string, double> > getModels();

private:
    std::shared_ptr<TcpClient> _client;
    std::vector<std::pair<std::string, double> > _models;
};

#endif