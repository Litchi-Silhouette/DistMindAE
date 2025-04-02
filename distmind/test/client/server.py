import time
import sys

import numpy as np
import torch

from py_utils.tcp import TcpServer

def main():
    address_for_client = sys.argv[1]
    port_for_client = int(sys.argv[2])

    server = TcpServer(address_for_client, port_for_client)
    while True:
        agent = server.tcpAccept()
        model_name_b = agent.tcpRecvWithLength()
        model_name = model_name_b.decode()
        data_b = agent.tcpRecvWithLength()
        data = torch.from_numpy(np.frombuffer(data_b, dtype=np.float32)).reshape(-1, 3, 224, 224)
        output = torch.sum(data, (1, 2, 3))
        output_b = output.numpy().tobytes()
        agent.tcpSendWithLength(output_b)


if __name__ == "__main__":
    main()