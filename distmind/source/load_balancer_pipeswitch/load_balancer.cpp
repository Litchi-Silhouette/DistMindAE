#include <unistd.h>
#include <string.h>

#include <string>
#include <memory>
#include <iostream>
#include <thread>
#include <queue>
#include <unordered_map>
#include <mutex>
#include <vector>

#include "tcp_pattern.h"
#include "controller_client.h"
#include "client_agent.h"
#include "server_agent.h"
#include "metadata_manager.h"

using namespace std;

struct AgentHandlerForClient: public AgentHandler {
    void run(shared_ptr<TcpAgent> agent);
};

shared_ptr<ControllerClient> _controller;
shared_ptr<MetadataManager> _metadata;
unordered_map<string, shared_ptr<ServerAgent> > _servers;

bool onceUpdateModelLocation();
void loopUpdateModelLocation();

int main(int argc, char** argv) {
    if (argc < 6) {
        cout << string("Argument Error") << endl;
        cout << string("program [ServerListFile] [AddrForClient] [PortForClient] [CtrlAddr] [CtrlPort]") << endl;
        return 0;
    }

    string server_list(argv[1]);
    string address_for_client(argv[2]);
    int port_for_client = stoi(argv[3]);
    string controller_address(argv[4]);
    int controller_port = stoi(argv[5]);
    
    _metadata.reset(new MetadataManager(server_list));
    for (string address: _metadata->getServerAddresses())
        _servers[address].reset(new ServerAgent(address));
    
    _controller.reset(new ControllerClient(controller_address, controller_port));
    thread thd_update(loopUpdateModelLocation);
    cout << "Connect to the controller" << endl << endl;
    
    TcpServerParallelWithAgentHandler s_client(address_for_client, port_for_client, shared_ptr<AgentHandler>(new AgentHandlerForClient()));
    cout << "Threads started" << endl;

    while (true)
        sleep(1);

    return 0;
}

void AgentHandlerForClient::run(shared_ptr<TcpAgent> agent) {
    shared_ptr<ClientAgent> client_agent(new ClientAgent(agent));

    shared_ptr<Message> request = client_agent->recvRequest();
    if (request == nullptr) {
        cout << "Request error" << endl;
        return;
    }

    string address = _metadata->forwardToLeastLoadedServer(request->model_name, 1);
    shared_ptr<ServerAgent> server = _servers[address];
    shared_ptr<Message> response = server->handleRequest(request);
    _metadata->decreaseWorkload(address);
    client_agent->sendResponse(response);
}

bool onceUpdateModelLocation() {
    auto notification = _controller->getNotification();
    // cout << "Get notification" << endl;
    _metadata->setServerPreference(notification.address, notification.model_name);
    // cout << "Update server model" << ", " << (unsigned int)notification.ip_int << ", " << notification.port << ", " << notification.model_name << endl;
    return true;
}

void loopUpdateModelLocation() {
    while (true)
        onceUpdateModelLocation();
}