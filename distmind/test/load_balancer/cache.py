import sys
import struct
import time
import socket

from source.py_utils.tcp import TcpClient

SIGNAL_CACHE_IN = 0
SIGNAL_CACHE_OUT = 1
SIGNAL_CACHE_REPLY = 2

def main():
    lb_addr = sys.argv[1]
    lb_port = int(sys.argv[2])

    client = TcpClient(lb_addr, lb_port)

    local_addr = '127.0.0.1'
    ip = struct.unpack('I', socket.inet_aton(local_addr))[0]
    port = 0
    capacity = 32 * 1024 * 1024 * 1024
    init_msg_b = struct.pack('IIQ', ip, port, capacity)
    client.tcpSend(init_msg_b)

    while True:
        op_b = client.tcpRecv(4)
        op = struct.unpack('I', op_b)[0]
        model_name_b = client.tcpRecvWithLength()
        model_name = model_name_b.decode()
        print (op, model_name)
        if op == SIGNAL_CACHE_IN:
            reply = SIGNAL_CACHE_REPLY
            reply_b = struct.pack('I', reply)
            client.tcpSend(reply_b)

if __name__ == "__main__":
    main()