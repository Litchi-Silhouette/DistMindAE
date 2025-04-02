from pssh.clients.native import ParallelSSHClient

import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ips", required=True, type=str)
    parser.add_argument("--lb-ip", required=True, type=str)


    return parser.parse_args()


def main():
    """"""
    args = get_args()

    ips = args.ips.split(',')
    pssh_clients = ParallelSSHClient(ips)

    cmds = ["conda activate pytorch-umem", 
            "cd ~/pipeps",
            "pkill python",
            "python source/mps/server_agent.py --lb-ip {} --lb-port 8778 --size-list ./model_sizes.txt".format(args.lb_ip)]
    cmd = ';'.join(cmds)
    outputs = pssh_clients.run_command(cmd)

    for host, host_output in outputs.items():
        for line in host_output.stdout:
            print("Host [%s] - %s" % (host, line))
        for line in host_output.stderr:
            print("Host [%s] - %s" % (host, line))


if __name__ == "__main__":
    main()