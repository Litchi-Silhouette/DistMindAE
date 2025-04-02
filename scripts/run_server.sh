source settings/config.sh

LOCAL_IP=$GLOBAL_LOCAL_IP
LOAD_BALANCER_IP=$GLOBAL_LOAD_BALANCER_IP

GPU_LIST="0 1 2 3 4 5 6 7"

CACHE_PORT=$GLOBAL_CAHCE_PORT_FOR_SERVER
LOAD_BALANCER_PORT=$GLOBAL_LOAD_BALANCER_PORT_FOR_SERVER

echo "GPU list: $GPU_LIST"
echo "Local IP: $LOCAL_IP"
echo "Load balancer IP: $LOAD_BALANCER_IP"
echo "Load balancer port: $LOAD_BALANCER_PORT"
sleep 1

for GPU in $GPU_LIST
do
    echo "Start worker $GPU"
	CUDA_VISIBLE_DEVICES=$GPU nohup python build/bin/server.py $LOCAL_IP 1001$GPU $LOCAL_IP $CACHE_PORT $LOAD_BALANCER_IP $LOAD_BALANCER_PORT >tmp/log_worker_$GPU.txt 2>&1 &
    sleep 1
done