import sys
import struct
import time

from source.py_utils.tcp import TcpClient

KVSTORAGE_OP_READ = 0
KVSTORAGE_OP_WRITE = 1
KVSTORAGE_OP_ACK = 2

def putKV(address, port, key, value):
    client = TcpClient(address, port)
    op = KVSTORAGE_OP_WRITE
    op_b = struct.pack('I', op)
    client.tcpSend(op_b)

    client.tcpSendWithLength(key.encode())
    client.tcpSendWithLength(value.encode())
    ret = client.tcpRecvWithLength().decode()
    print (ret)

def getKV(address, port, key):
    client = TcpClient(address, port)
    op = KVSTORAGE_OP_READ
    op_b = struct.pack('I', op)
    client.tcpSend(op_b)

    client.tcpSendWithLength(key.encode())
    ret = client.tcpRecvWithLength().decode()
    print (ret)
    return ret

def main():
    address = sys.argv[1]
    port = int(sys.argv[2])
    putKV(address, port, 'abc', 'def')
    time_1 = time.time()
    getKV(address, port, 'abc')
    time_2 = time.time()
    print (time_2 - time_1)


if __name__ == "__main__":
    main()