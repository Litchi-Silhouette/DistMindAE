import sys
import struct
import time
import socket

import numpy as np
import torch

from source.py_utils.tcp import TcpClient

def main():
    lb_addr = sys.argv[1]
    lb_port = int(sys.argv[2])

    client = TcpClient(lb_addr, lb_port)

    local_addr = '127.0.0.1'
    ip = struct.unpack('I', socket.inet_aton(local_addr))[0]
    port = 0
    init_msg_b = struct.pack('II', ip, port)
    client.tcpSend(init_msg_b)

    while True:
        model_name_b = client.tcpRecvWithLength()
        model_name = model_name_b.decode()
        print (model_name)
        data_b = client.tcpRecvWithLength()
        data = torch.from_numpy(np.frombuffer(data_b, dtype=np.float32)).reshape(-1, 3, 224, 224)
        output = data.sum((1, 2, 3))
        output_b = output.numpy().tobytes()
        client.tcpSendWithLength(output_b)

if __name__ == "__main__":
    main()