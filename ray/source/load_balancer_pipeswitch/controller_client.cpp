#include <unistd.h>

#include <string>

#include "controller_client.h"

using namespace std;

ControllerClient::ControllerClient(string addr, int port):
_client(new TcpClient(addr, port)) {
    size_t num_models = 0;
    _client->tcpRecv((char*)(&num_models), sizeof(num_models));
    for (int i = 0; i < num_models; ++i) {
        string model_name;
        _client->tcpRecvString(model_name);
        double model_prob;
        _client->tcpRecv((char*)&model_prob, sizeof(model_prob));
        _models.push_back(make_pair(model_name, model_prob));
    }
}

ControllerClient::~ControllerClient() {}

ControllerUpdateNotification ControllerClient::getNotification() {
    ControllerUpdateNotification notification;
    _client->tcpRecvString(notification.address);
    _client->tcpRecvString(notification.model_name);
    
    int reply = 1;
    _client->tcpSend((char*)&reply, sizeof(reply));

    return notification;
}

const vector<pair<string, double> > ControllerClient::getModels() {
    return _models;
}