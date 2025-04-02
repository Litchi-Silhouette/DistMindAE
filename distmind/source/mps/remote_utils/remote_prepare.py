from pssh.clients.native import ParallelSSHClient

import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ips", required=True, type=str)

    return parser.parse_args()

def main():
    """ launch 
    """
    args = get_args()

    ips = args.ips.split(',')
    # assume current instance has permission to ssh into all others
    pssh_clients = ParallelSSHClient(ips)

    cmds = ["conda activate pytorch-umem", 
            "cd pipeps",
            "python source/mps/load_models.py build/resources/model_list.txt ./model_sizes.txt",
            "python source/mps/launch_mps_daemon.py"]

    cmd = ";".join(cmds)

    outputs = pssh_clients.run_command(cmd)

    for host, host_output in outputs.items():
        for line in host_output.stdout:
            print("Host [%s] - %s" % (host, line))
        for line in host_output.stderr:
            print("Host [%s] - %s" % (host, line))


if __name__ == "__main__":
    main()