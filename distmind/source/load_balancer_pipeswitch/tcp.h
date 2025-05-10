#ifndef BALANCE_TCP_H
#define BALANCE_TCP_H

#include <unistd.h>

#include <string>
#include <memory>

class TcpServer;
class TcpAgent;
class TcpClient;

const int ERRNO_SUCCESS = 0;
const int ERRNO_TCP = 1;

std::string ip_int2str(int ip_int);
int ip_str2int(std::string ip);

class TcpServer {
public:
    TcpServer(std::string address, int port, int listen_num = 4);
    ~TcpServer();
    std::shared_ptr<TcpAgent> tcpAccept();
private:
    std::string _address;
    int _port;
    int _server_fd;
};

class TcpAgent {
public:
    TcpAgent(int conn_fd);
    ~TcpAgent();

    int tcpSend(const char* data, size_t size);
    int tcpRecv(char* data, size_t size);
    int tcpSendWithLength(const char* data, size_t size);
    int tcpSendWithLength(const std::shared_ptr<char> data, size_t size);
    int tcpRecvWithLength(std::shared_ptr<char> &data, size_t &size);
    int tcpSendString(const std::string data);
    int tcpRecvString(std::string &data);

protected:
    int _conn_fd;
};

class TcpClient: public TcpAgent {
public:
    TcpClient(std::string address, int port);
    ~TcpClient();
private:
    std::string _address;
    int _port;
};

#endif