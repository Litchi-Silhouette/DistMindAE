#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <netinet/tcp.h>

#include <string>
#include <memory>
#include <iostream>

#include "utils/common/errno.h"

#include "tcp.h"


namespace balance {
namespace util {

using namespace std;

TcpServer::TcpServer(string address, int port, int listen_num):
_address(address), _port(port) {
    _server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (_server_fd == 0) { 
        perror("util/common/TCPServer CreateSocket");
        exit(EXIT_FAILURE); 
    } 
       
    int opt = 1;
    if (setsockopt(_server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) { 
        perror("util/common/TCPServer SetSocketOption");
        exit(EXIT_FAILURE); 
    }
    int yes = 1;
    if (setsockopt(_server_fd, IPPROTO_TCP, TCP_NODELAY, &yes, sizeof(yes))) { 
        perror("util/common/TCPServer SetSocketOption");
        exit(EXIT_FAILURE); 
    }

    struct sockaddr_in addr;
    addr.sin_family = AF_INET; 
    addr.sin_port = htons(_port);
    if(inet_pton(AF_INET, _address.c_str(), &addr.sin_addr) <= 0) { 
        perror("util/common/TCPServer ConvertStringAddress");
        exit(EXIT_FAILURE);
    }
    if (bind(_server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) { 
        perror("util/common/TCPServer BindPort");
        exit(EXIT_FAILURE); 
    } 
    if (listen(_server_fd, listen_num) < 0) {
        perror("util/common/TCPServer Listen");
        exit(EXIT_FAILURE); 
    } 
}

TcpServer::~TcpServer() {
    close(_server_fd);
}

shared_ptr<TcpAgent> TcpServer::tcpAccept() {
    int conn_fd;
    struct sockaddr_in addr;
    size_t addrlen = sizeof(addr);
    conn_fd = accept(_server_fd, (struct sockaddr *)&addr, (socklen_t*)&addrlen);
    if (conn_fd < 0) {
        perror("util/common/TCPServer AcceptConnection");
        exit(EXIT_FAILURE); 
    }

    return shared_ptr<TcpAgent>(new TcpAgent(conn_fd));
}

TcpAgent::TcpAgent(int conn_fd): _conn_fd(conn_fd) { }

TcpAgent::~TcpAgent() {
    shutdown(_conn_fd, SHUT_RDWR);
    close(_conn_fd);
}

int TcpAgent::tcpSend(const char* data, size_t size) {
    auto ret = send(_conn_fd, data, size , 0);
    if (ret != size)
        sleep(600);
    return ERRNO_SUCCESS;
}

int TcpAgent::tcpRecv(char* data, size_t size) {
    auto ret = recv(_conn_fd, data, size, MSG_WAITALL);
    if (ret != size)
        sleep(600);
    return ERRNO_SUCCESS;
}

int TcpAgent::tcpSendWithLength(const char* data, size_t size) {
    tcpSend((char*)&size, sizeof(size) );
    tcpSend(data, size);
    return ERRNO_SUCCESS;
}

int TcpAgent::tcpSendWithLength(const shared_ptr<char> data, size_t size) {
    tcpSend((char*)&size, sizeof(size) );
    tcpSend(data.get(), size);
    return ERRNO_SUCCESS;
}

int TcpAgent::tcpRecvWithLength(shared_ptr<char> &data, size_t &size) {
    tcpRecv((char*)&size, sizeof(size));
    data.reset((char*)malloc(size));
    tcpRecv(data.get(), size);
    return ERRNO_SUCCESS;
}

int TcpAgent::tcpSendString(const string data) {
    size_t data_size = data.size();
    tcpSend((char*)&data_size, sizeof(data_size));
    tcpSend(data.c_str(), data_size);
    return ERRNO_SUCCESS;
}

int TcpAgent::tcpRecvString(string &data) {
    size_t data_size = 0;
    tcpRecv((char*)&data_size, sizeof(data_size));
    char* buffer = (char*)malloc(data_size);
    memset(buffer, 0, data_size);
    tcpRecv(buffer, data_size);
    data = string(buffer, data_size);
    free(buffer);
    return ERRNO_SUCCESS;
}

TcpClient::TcpClient(string address, int port):
TcpAgent(0), _address(address), _port(port) {
    _conn_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (_conn_fd == 0) { 
        perror("util/common/TCPClient CreateSocket");
        exit(EXIT_FAILURE);
    }

    int yes = 1;
    if (setsockopt(_conn_fd, IPPROTO_TCP, TCP_NODELAY, &yes, sizeof(yes))) { 
        perror("util/common/TCPServer SetSocketOption");
        exit(EXIT_FAILURE); 
    }

    struct sockaddr_in serv_addr; 
    serv_addr.sin_family = AF_INET; 
    serv_addr.sin_port = htons(_port);
    if(inet_pton(AF_INET, _address.c_str(), &serv_addr.sin_addr) <= 0) { 
        perror("util/common/TCPClient ConvertStringAddress");
        exit(EXIT_FAILURE);
    }
    if (connect(_conn_fd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) { 
        perror("util/common/TCPClient MakeConnection");
        exit(EXIT_FAILURE);
    } 
}

TcpClient::~TcpClient() {
    ;
}

} //namespace util
} //namespace balance