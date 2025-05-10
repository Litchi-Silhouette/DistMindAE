import requests
import threading
import numpy as np
from enum import Enum
import time
import argparse

from tcp import TcpClient
from ssh_comm import get_host_ips

def get_args():
    """"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--hostfile", required=True)
    parser.add_argument("--output-stats", required=True, help="output the throughput statistic")
    parser.add_argument("--output-req-log", default="requests_log.txt")
    parser.add_argument("--interval", default=1, type=int, help="statistic interval in seconds")

    return parser.parse_args()

def inference_query(ip, port, gpu_id, model_idx):
    query_url = f"http://{ip}:{port}/gpu-{gpu_id}/inference/{model_idx}"
    resp = requests.get(query_url)
    return resp

def query_inference_count(ip, port, gpu_id, results):
    url=f"http://{ip}:{port}/gpu-{gpu_id}/inference_count"
    resp = requests.get(url)
    while resp.status_code != 200:
        resp = requests.get(url)

    key = f'{ip}:{gpu_id}'
    results[key] = resp.json()['count']

def query_training_count(ip, port, gpu_id, results):
    url=f"http://{ip}:{port}/gpu-{gpu_id}/training_batch_count"
    resp = requests.get(url)
    while resp.status_code != 200:
        resp = requests.get(url)

    key = f'{ip}:{gpu_id}'
    results[key] = resp.json()['count']

class Workload(Enum):
    NULL = 0
    INFERENCE = 1
    TRAINING = 2

class WorkloadGenerator:

    def __init__(self, ip, port, gpu_id, log_file=None):
        """"""
        self.log_file = log_file
        if self.log_file is not None:
            self.log_file = open(self.log_file, 'w')

        self.shutdown = False
        self.inf_bs = 8
        self.node_ip = ip
        self.node_port = port
        self.gpu_id = gpu_id

        self.query_data = np.random.rand(self.inf_bs, 3, 224, 224).astype(np.float32).tobytes()
        self.workload : Workload = Workload.NULL
        self.gpu_is_training = False

        self.inference_model_id = -1
        self.last_inference_model_id = -1
        self.workload_lock = threading.RLock()

        self.daemon_thd = threading.Thread(target=self._background, args=())
        self.daemon_thd.start()

        self.inference_history = []
    
    def log(self, msg):
        out_msg = f"GPU {self.node_ip}:{self.gpu_id} => {msg}"
        if self.log_file is None:
            print(out_msg)
        else:
            self.log_file.write(f"{out_msg}\n")
    
    def _background(self,):
        while not self.shutdown:
            """"""
            if self.workload == Workload.INFERENCE:
                """make inference request """
                self.log(f'workload {self.workload}')
                with self.workload_lock:
                    model_id = self.inference_model_id
                inf_start = time.time()
                self.log(f'query inf {model_id}')
                resp = inference_query(self.node_ip, self.node_port, 
                                        self.gpu_id, model_id)
                inf_end = time.time()
                try:
                    self.log(resp.json())
                    self.inference_history.append(
                        [inf_start, inf_end, model_id]
                    )
                    self.log(f'Inference takes {(inf_end - inf_start) * 1e3}ms')
                except:
                    self.log(f"Inference request failed {resp}")
                
                self.last_inference_model_id = model_id

            elif self.workload == Workload.TRAINING:
                """ launch training """
                self.launch_training()
                self.last_inference_model_id = -1
            else:
                time.sleep(0.005)
    
    
    def launch_training(self):
        if self.gpu_is_training:
            return
        resp = requests.get(url=f"http://{self.node_ip}:{self.node_port}/gpu-{self.gpu_id}/train")
        try:
            self.log("start training" + resp.json())
            self.gpu_is_training = True
        except:
            self.log(f'start training failed resp {resp}')
            pass

    def set_workload(self, workload: Workload, inference_model_id=-1,):
        with self.workload_lock:
            self.workload = workload
            if self.workload == Workload.INFERENCE:
                assert inference_model_id != -1
                self.inference_model_id = inference_model_id
                print(f'set inference model id {self.inference_model_id}')
    
def stats_thread_fn(interval, output_file, node_ips, ngpus, port):
    last_inference_counts = {}
    last_training_counts = {}

    log_file = open(output_file, 'w')

    while True:
        t_start = time.time()
        cur_inference_counts = {}
        cur_training_counts = {}
        query_threads = []
        for ip in node_ips:
            for i in range(ngpus):
                inf_t = threading.Thread(
                    target=query_inference_count, 
                    args=(ip, port, i, cur_inference_counts))
                inf_t.start()
                train_t = threading.Thread(
                    target=query_training_count,
                    args=(ip, port, i, cur_training_counts))
                train_t.start()
                query_threads.append(inf_t)
                query_threads.append(train_t)

        for t in query_threads:
            t.join()
        # compute the difference
        if len(last_inference_counts) > 0:
            throughputs = []
            for key in cur_training_counts:
                d_inf = cur_inference_counts[key] - last_inference_counts[key]
                d_train = cur_training_counts[key] - last_training_counts[key]
                throughputs.append(d_inf)
                throughputs.append(d_train)
            # write out
            output_str = ", ".join([str(v) for v in throughputs])
            print(f'throughput:: {output_str}')
            log_file.write(f"{time.time()}, {output_str}\n")
            log_file.flush()
        
        last_inference_counts = cur_inference_counts
        last_training_counts = cur_training_counts
        t_end = time.time() 
        pause_time = interval - (t_end - t_start)
        if pause_time > 0:
            print(f"sleep for {pause_time}")
            time.sleep(pause_time)

def main():
    """"""
    controller_ip = "127.0.0.1"
    controller_port = 9004
    # assume each have 8 GPUs
    n_gpus = 8
    server_port = 8000
    args = get_args()
    node_ips = get_host_ips(args.hostfile)

    # start the stats gathering thread
    stats_thd = threading.Thread(
                    target=stats_thread_fn, 
                    args=(args.interval, args.output_stats, node_ips, n_gpus, server_port))

    stats_thd.start()

    req_generators = {}
    for i in range(len(node_ips)): 
        for j in range(n_gpus):
            _id = f"{node_ips[i]}:{j}"
            req_generators[_id] = WorkloadGenerator(
                node_ips[i], server_port, j, log_file=f"{args.output_req_log}-{_id}")

    # connect to controller to get the workload
    controller_cli = TcpClient(controller_ip, controller_port)

    while True:
        server_id = controller_cli.tcpRecvWithLength().decode("utf-8")
        model_name:str = controller_cli.tcpRecvWithLength().decode("utf-8")
        controller_cli.tcpSend(b"RECV")
        print(f'{time.time()}: {server_id} {model_name}')

        g: WorkloadGenerator = req_generators[server_id]
        if "alter" in model_name:
            id_ = int(model_name.rsplit("-", 1)[-1])
            print(f'changing workload to {model_name}')
            g.set_workload(Workload.INFERENCE, id_)
        elif "train" in model_name:
            id_ = -1
            g.set_workload(Workload.TRAINING, id_)
        else:
            print(f"unknown workload for {server_id}: {model_name}")

if __name__ == "__main__":
    main()