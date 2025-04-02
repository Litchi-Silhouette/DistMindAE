"""
"""
import argparse
import logging
import queue
import random
import sys
import threading as thd
import time
from typing import Dict

import numpy as np

import source.mps.lru as lru
import source.py_utils.tcp as tcp
from source.controller import controller_agent


def sch_strategy(loads, loads_mtx, localLRU, localLRU_mtx, cache_loc, cache_loc_mtx, model_name, server_map):
    """ return gpu-id, evict[gpu-id, model-name], launch[gpu-id, model-name]"""

    avaiable_GPUs = server_map.valid_server_list()
    GPU_ids = list(loads.keys())
    # print('GPU_ids', GPU_ids)
    avaiable_GPUs = list([GPU_ids[i] for i in avaiable_GPUs])
    print("size of available GPUs", len(avaiable_GPUs))

    def get_with_cache(model_name, cache_loc, loads):
        if model_name in cache_loc:
            gpu_ids = list(cache_loc[model_name])
            gpu_ids = list(set(gpu_ids).intersection(set(avaiable_GPUs)))
            if len(gpu_ids) < 1:  # model cache deleted all
                return None
            min_load_id = gpu_ids[0]
            for gid in gpu_ids:
                with loads_mtx:
                    if loads[gid] < loads[min_load_id]:
                        min_load_id = gid
            return min_load_id
        else:
            return None

    def update_cacheloc(cache_loc, evict, launch):
        if evict:
            model_name = evict[1]
            gpu_id = evict[0]
            cache_loc[model_name].remove(gpu_id)
        if launch:
            model_name = launch[1]
            gpu_id = launch[0]
            if model_name in cache_loc:
                cache_loc[model_name].add(gpu_id)
            else:
                cache_loc[model_name] = set([gpu_id])

    def get_idle_gpus(loads):
        idle = []
        for gpu in loads.keys():
            with loads_mtx:
                if loads[gpu] < 1 and (gpu in avaiable_GPUs):
                    idle.append(gpu)
        return idle
    
    with cache_loc_mtx and loads_mtx and localLRU_mtx:
        gpu_id = get_with_cache(model_name, cache_loc, loads)

        if gpu_id:
            # cache hit
            # move cache to recent
            lcache = localLRU[gpu_id]
            _ = lcache.get(model_name)
            return gpu_id, [], []

        idle = get_idle_gpus(loads)
        while len(idle) == 0:
            time.sleep(0.0001)
            idle = get_idle_gpus(loads)

        for gpu in idle:
            lcache = localLRU[gpu]

            val = lcache.get(model_name)
            if val != -1:
                # cache hit
                return gpu, [], []
            else:
                # cache miss
                pass
        # launch a cache program at min_cache_size_gpu
        min_cache_size_gpu = random.choice(idle) # random choose one
        launch = [min_cache_size_gpu, model_name]
        evict = []
   
        evict_model = localLRU[min_cache_size_gpu].put(model_name, model_name)
        if evict_model:
            evict = [min_cache_size_gpu, evict_model]
        update_cacheloc(cache_loc, evict, launch)

    return min_cache_size_gpu, evict, launch



class LoadBalancer:

    def __init__(self, cliPort, serverPort, server_map, fillWithTraining=False):
        """"""
        self.server_map = server_map

        self.fillWithTraining = fillWithTraining

        # after dispatched to gpu server
        self.processed_requests_mtx = thd.Lock()
        self.processed_requests = dict()
        self.incoming_requests = queue.Queue()  # from clients

        self.loads = dict()  # [gpu-id, task-count]
        self.loads_mtx = thd.Lock()
        self.workers = dict()  # [gpu-id, tcp-conn]
        self.workers_mtx = thd.Lock()
        self.worker_conn_mtxs = dict()

        self.trainingStatus = dict()  # [gpu-id, int]
        self.trainingStatus_mtx = thd.Lock()
        self.instance = dict()
        self.gpu_belong = dict()

        self.gpu_LRUCache = dict()  # [gpu-id, lru.LRUCache]
        self.gpu_LRUCache_mtx = thd.Lock()
        self.cache_loc = dict()
        self.cache_loc_mtx = thd.Lock()
        
        self.request_id = 0
        self.request_id_mtx = thd.Lock()

        # client tcp server
        tcp_server = tcp.TcpServer('0.0.0.0', cliPort)
        server_lock = thd.Lock()
        for _ in range(8): # process pool for tcp acceptance
            cli_tcp_thd = thd.Thread(target=self._towardsClient, 
                                        args=(tcp_server, server_lock, self.incoming_requests))
            cli_tcp_thd.start()

        # server tcp server
        serv_tcp_proc = thd.Thread(
            target=self._towardsGPUServerThd, args=(serverPort,))
        serv_tcp_proc.start()

    def run(self,):
        """ the main function loop
        handle request from client
        dispatch it to GPU servers
        """
        n_proc = 8
        if self.fillWithTraining:
            """ start _fiilTrainingThd"""
            logging.debug("starting fill with training")
            _trainProc = thd.Thread(target=self._fillTrainingThd)
            _trainProc.start()
            logging.debug('fill Training started proc')

        request_consumers = []
        for _ in range(n_proc):
            p = thd.Thread(target=self._req_handl_proc)
            p.start()
            request_consumers.append(p)
        
        for p in request_consumers:
            p.join()

    def _towardsClient(self, server, server_lock, request_q):
        """ launch as a Process """

        while True:
            server_lock.acquire()
            conn = server.tcpAccept()
            server_lock.release()
            model_name = conn.tcpRecvWithLength()
            data = conn.tcpRecvWithLength()
            request_q.put([model_name, data, conn])
            logging.debug('client request model %s', model_name)

    def _towardsGPUServerThd(self, port):
        """ it need to modify the LB status
        accept connections from gpu servers
        receive GPU ids
        save connection obj
        """
        server = tcp.TcpServer('0.0.0.0', port)
        logging.info('tcp server for GPU servers started')
        while True:
            conn = server.tcpAccept()
            conn_mtx = thd.Lock()
            # register gpu ids
            gpus = conn.tcpRecvWithLength()
            self._registerGPUs(gpus, conn)

            # start threads to monitor response
            for _ in range(4):
                _p = thd.Thread(target=self._responseReaderProc,
                                    args=(conn, conn_mtx))
                _p.start()

    def _registerGPUs(self, gpus, conn):
        gpus = gpus.decode().split(';')
        conn_lck = thd.Lock()
        inst_idx = len(self.instance)
        self.instance[inst_idx] = {'gpus': gpus, 'training': False}
        for g in gpus:
            self.gpu_belong[g] = inst_idx
            with self.workers_mtx:
                self.workers[g] = conn
                self.worker_conn_mtxs[g] = conn_lck

            with self.loads_mtx:
                self.loads[g] = 0
            # assume 10 client process
            self.gpu_LRUCache[g] = lru.LRUCache(15)
            logging.info('registered gpu %s', g)

            # if self.fillWithTraining
            # send start training proc message
            # init self.trainingStatus for each gpu
            # self.trainingStatus will be marked to 1 by fillTrainingThd
            if self.fillWithTraining:
                conn.tcpSendWithLength(b'create_train_proc')
                # conn.tcpSendWithLength(g.encode())

                # self.trainingStatus[g] = 0
                # logging.debug('training stats keys %s', self.trainingStatus.keys())

    def _responseReaderProc(self, conn: tcp.TcpAgent, conn_mtx):  # pylint: disable=no-member
        """ read response from GPU server in thread
        and put it in res_q
        """
        while True:
            with conn_mtx:
                req_id = int(conn.tcpRecvWithLength().decode())
                cache_id = conn.tcpRecvWithLength().decode()  # gpu-id+model-name
                outputs = conn.tcpRecvWithLength()
            # reduce worker load
            gpu_id, _ = cache_id.split('$$')
            with self.loads_mtx:
                self.loads[gpu_id] -= 1

            # response to client directly
            with self.processed_requests_mtx:
                cli_conn = self.processed_requests[req_id]
                cli_conn.tcpSendWithLength(outputs)
            del self.processed_requests[req_id]
            del cli_conn
            logging.debug("reponsed %s", req_id)

    def _req_handl_proc(self, ):
        server_map = self.server_map

        ts_req = []
        while True:
            t1 = time.time()
            req = self.incoming_requests.get()
            # make sure while processing, training monitor will not send start training
            
            model_name = req[0].decode()
            t1 = time.time()
            # schedule it
            logging.debug("handle one incoming request %s", model_name)
            gpu_id, evict, launch = sch_strategy(self.loads, self.loads_mtx, self.gpu_LRUCache, self.gpu_LRUCache_mtx, self.cache_loc, self.cache_loc_mtx,
                                                     model_name, server_map)
            
            if evict:
                logging.debug(
                    'need to eviting on gpu %s, with model %s', evict[0], evict[1])
                with self.workers_mtx:
                    conn = self.workers[evict[0]]
                
                with self.worker_conn_mtxs[evict[0]]:
                    conn.tcpSendWithLength(b'evict')
                    conn.tcpSendWithLength(
                        "{}$${}".format(evict[0], evict[1]).encode())
            if launch:
                logging.debug(
                    'need to launch on gpu %s, with model %s', launch[0], launch[1])
                with self.workers_mtx:
                    conn = self.workers[launch[0]]
                with self.worker_conn_mtxs[launch[0]]:
                    conn.tcpSendWithLength(b'create')
                    conn.tcpSendWithLength(launch[0].encode())
                    conn.tcpSendWithLength(launch[1].encode())
            
            with self.workers_mtx:
                conn = self.workers[gpu_id]

            with self.request_id_mtx:
                self.request_id += 1
                request_id = self.request_id

            with self.worker_conn_mtxs[gpu_id]:
                conn.tcpSendWithLength(b'inf')
                conn.tcpSendWithLength(str(request_id).encode())
                conn.tcpSendWithLength(
                    "{}$${}".format(gpu_id, model_name).encode())
                conn.tcpSendWithLength(req[1])

            # maintain tcp connection for response
            with self.processed_requests_mtx:
                self.processed_requests[request_id] = req[2]
            with self.loads_mtx:
                self.loads[gpu_id] += 1

            ts_req.append(time.time() - t1)
            if (len(ts_req) % 100 == 0):
                logging.info('avg request handle cost %s s', np.mean(ts_req[-100:]))
            logging.debug(
                'dispatched task to gpu id %s, request id %s', gpu_id, request_id)
    
    def _fillTrainingThd(self,):
        """ check self.incoming_requests queue, 
        if it is empty and some self.loads[gpu-id] is 0
            start training on that gpu
        """
  
        # server_map = controller_agent.listenController(controller_address, controller_port, lambda model_name: 'train' not in model_name)
        server_map = self.server_map
        
        logging.info("_fillTrainingProc")
        logging.debug('monite for necessary training')

        while True:
            inf_gpu_idxs = server_map.valid_server_list()
            with self.loads_mtx:
                GPU_ids = list(self.loads.keys())

            inf_GPUs = []
            for i in inf_gpu_idxs:
                if i < len(GPU_ids):
                    inf_GPUs.append(GPU_ids[i])

            train_GPUs = list(set(GPU_ids) - set(inf_GPUs))
            # logging.debug('gpus for inference size %s', len(inf_GPUs))
            # map selected gpus to instance ids
            instances = list([len(self.instance[i]['gpus']) for i in range(len(self.instance))])
            need_training_signal = []
            for gpu_id in train_GPUs:
                inst_idx = self.gpu_belong[gpu_id]
                instances[inst_idx] -= 1

                if instances[inst_idx] == 0:
                    need_training_signal.append(inst_idx)
            
            logging.debug("need_training_signal %s", str(need_training_signal))
            for idx in self.instance:
                if idx in need_training_signal:
                    if not self.instance[idx]['training']:
                        _gpu_id = self.instance[idx]['gpus'][0] # any gpu is fine
                        conn = self.workers[_gpu_id]
                        with self.worker_conn_mtxs[_gpu_id]:
                            conn.tcpSendWithLength(b'start_training')
                            self.instance[idx]['training'] = True
                        logging.debug('sending start training to instance %s', idx)
                else:
                    if self.instance[idx]['training']:
                        _gpu_id = self.instance[idx]['gpus'][0] # any gpu is fine
                        conn = self.workers[_gpu_id]
                        with self.worker_conn_mtxs[gpu_id]:
                            conn.tcpSendWithLength(b'stop_training')
                            self.instance[idx]['training'] = False
                        logging.debug('sending stop training to instance %s', idx)
            
            time.sleep(0.1)


def main():
    """"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--fill-train", action='store_true')
    parser.add_argument("--debug", action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)

    controller_address = "127.0.0.1"
    controller_port = 9004
    server_map = controller_agent.listenController(controller_address, controller_port, lambda model_name: 'train' not in model_name)

    lb = LoadBalancer(8777, 8778, server_map, args.fill_train)
    lb.run()


if __name__ == "__main__":
    main()
