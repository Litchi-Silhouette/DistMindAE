import source.py_utils.tcp as tcp
import posix_ipc
import pickle
import mmap
from multiprocessing.reduction import ForkingPickler
import numpy as np
import threading as thd
from queue import Queue
import time
import os


def loop_recv_thd(cli_q:Queue):
    while True:
        cli = cli_q.get()
        resp = cli.tcpRecvWithLength()
        print(resp)


def send_req(fake_data):
    cli = tcp.TcpClient("127.0.0.1", 9999)
    cli.tcpSendWithLength(b'modelxxxxxxx')
    cli.tcpSendWithLength(fake_data)
    resp = cli.tcpRecvWithLength()
    print(resp)


def make_request_async(fake_data):
    t = thd.Thread(target=send_req, args=(fake_data,))
    t.start()
    return t


def main():
    """"""
    fake_data = np.random.rand(8, 3,224,224).tobytes()
    cli_q = Queue()
    resp_thd = thd.Thread(target=loop_recv_thd, args=(cli_q,))
    resp_thd.start()
    
    avg_ts = []
    while True:
        t1 = time.time()
        make_request_async(fake_data)
        time.sleep(0.005)

        avg_ts.append(time.time() - t1)
        if len(avg_ts) % 10 == 0:
            a = np.mean(avg_ts[-100:])*1e3
            print('avg time %s ms' % a)


main()