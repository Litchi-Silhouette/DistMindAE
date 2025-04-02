import sys
import time
import struct
import socket

from source.py_utils.tcp import TcpServer

SIGNAL_CACHE_IN = 0
SIGNAL_CACHE_OUT = 1
SIGNAL_CACHE_REPLY = 2

def main():
    listen_addr = sys.argv[1]
    listen_port = int(sys.argv[2])

    server = TcpServer(listen_addr, listen_port)
    agent = server.tcpAccept()
    cache_info_b = agent.tcpRecv(16)
    cache_addr = socket.inet_ntoa(cache_info_b[:4])
    cache_port = struct.unpack('I', cache_info_b[4:8])[0]
    capacity = struct.unpack('Q', cache_info_b[8:])[0]
    print ('Cache Info', cache_addr, cache_port, capacity)
    time.sleep(1)

    model_name = 'resnet152'
    op_b = struct.pack('I', SIGNAL_CACHE_IN)
    agent.tcpSend(op_b)
    agent.tcpSendWithLength(model_name.encode())
    reply_signal_b = agent.tcpRecv(4)
    reply_signal = struct.unpack('I', reply_signal_b)[0]
    print (reply_signal)
    time.sleep(1)

    while True:
        time.sleep(600)

if __name__ == "__main__":
    main()