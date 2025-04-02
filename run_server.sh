LOCAL_IP=$1
REMOTE_IP=$2

echo "Local IP: $LOCAL_IP"
echo "Remote IP: $REMOTE_IP"
sleep 1

for GPU in {0..7}
do
    echo "Start worker $GPU"
	CUDA_VISIBLE_DEVICES=$GPU nohup python build/bin/server.py $LOCAL_IP 1001$GPU $LOCAL_IP 10009 $REMOTE_IP 8889 >tmp/log_worker_$GPU.txt 2>&1 &
    sleep 1
done