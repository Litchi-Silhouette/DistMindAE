#include <unistd.h>
#include <string.h>
#include <arpa/inet.h>

#include <string>

#include "lb_agent.h"

using namespace std;
using namespace balance::util;

LBAgent::LBAgent(std::string lb_addr, int lb_port, std::string addr_for_ser, size_t capability) {
    _tcp.reset(new TcpClient(lb_addr, lb_port));

    struct {
        int ip_int;
        int port;
        size_t capacity;
    } cache_info;
    inet_pton(AF_INET, addr_for_ser.c_str(), &(cache_info.ip_int));
    cache_info.port = 0;
    cache_info.capacity = capability;
    _tcp->tcpSend((char*)&cache_info, sizeof(cache_info));
}

LBAgent::~LBAgent() {

}

shared_ptr<LBInstruction> LBAgent::getInstruction() {
    int op;
    _tcp->tcpRecv((char*)&op, sizeof(op));

    string model_name;
    _tcp->tcpRecvString(model_name);

    return shared_ptr<LBInstruction>(new LBInstruction(op, model_name));
}

void LBAgent::replySignal() {
    int signal_reply = 0;
    _tcp->tcpSend((char*)&signal_reply, sizeof(signal_reply));
}