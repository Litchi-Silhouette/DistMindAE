import source.py_utils.tcp as tcp
import posix_ipc
import pickle
import mmap
from multiprocessing.reduction import ForkingPickler
import torch.multiprocessing as mp
from source.mps.mp_queue import SHMQueue
import time
import numpy as np
import threading as thd
import logging

logging.basicConfig(
            format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.DEBUG)

def _proc_consumer(mq):
    # mq = SHMQueue(qname, False)

    ts = []
    while True:
        t1 = time.time()
        model, data, conn = mq.get()
        ts.append(time.time() - t1)
        logging.debug('get a msg')
        print('get data with length %s' % len(data))
        conn.tcpSendWithLength(b"receive req" + model)

        
        if len(ts) % 20 == 0:
            a = np.mean(ts[-100:])*1e3
            print('avg time %s ms' % a)



def _tcp_server_thd(qname, tcp_server, tcp_lock:thd.Lock, mq):

    # mq = SHMQueue(qname, False)
    while True:
        tcp_lock.acquire()
        conn = tcp_server.tcpAccept()
        tcp_lock.release()
        model_name = conn.tcpRecvWithLength()
        data = conn.tcpRecvWithLength()

        mq.put([model_name, data, conn])
        logging.debug("put a msg")


def main():
    qname = '/test_shmq'

    # mq = SHMQueue(qname, True)
    mq = mp.Queue()

    cs = []
    for _ in range(1):
        consumer = mp.Process(target=_proc_consumer, args=(mq,))
        consumer.start()
        cs.append(consumer)

    server = tcp.TcpServer('0.0.0.0', 9999)
    server_lck = mp.Lock()
    for _ in range(4):
        t = mp.Process(target=_tcp_server_thd, args=(qname, server, server_lck, mq))
        t.start()
    
    t.join()

if __name__ == "__main__":
    main()
