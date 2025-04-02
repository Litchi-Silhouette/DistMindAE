import sys
import struct
import threading

from py_utils.tcp import TcpServer
from controller_agent import listenController

def thd_func_loop_accept_gpu(address, port, map, lock):
    server = TcpServer(address, port)
    while True:
        agent = server.tcpAccept()
        server_id_b = agent.tcpRecv(8)
        ip_int, port = struct.unpack('II', server_id_b[0:8])
        lock.acquire()
        if ip_int not in map:
            map[ip_int] = {}
        map[ip_int][port] = agent
        lock.release()

def main():
    address = sys.argv[1]
    port = sys.argv[2]
    ctrl_addr = sys.argv[3]
    ctrl_port = sys.argv[4]

    gpu_map = {}
    gpu_map_lock = threading.Lock()

    # Thread 1: Accept training processes
    thd_accept_gpu = threading.Thread(target=thd_func_loop_accept_gpu, args=(address, port, gpu_map, gpu_map_lock))
    thd_accept_gpu.start()

    # Thread 2: Accept controller notifications
    def callback_update_model(ip_int, port, model_name):
        if ip_int in gpu_map:
            for port in gpu_map[ip_int]:
                agent = gpu_map[ip_int][port]
                agent.tcpSendWithLength(model_name.encode())
                _ = agent.tcpRecv(4)
    _ = listenController(ctrl_addr, ctrl_port, None, callback_update_model)

    thd_accept_gpu.join()

if __name__ == "__main__":
    main()