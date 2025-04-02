import argparse
from ssh_comm import get_host_ips

def get_args():
    """"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--hostfile", required=True)
    parser.add_argument("--output", default="server_list.txt")

    return parser.parse_args()

def main():
    """"""
    args = get_args()

    host_ips = get_host_ips(args.hostfile)
    ngpus = 8
    with open(args.output, 'w') as out_file:
        for ip in host_ips:
            for gpu_idx in range(ngpus):
                out_file.write(f"{ip}:{gpu_idx}\n")


if __name__ == "__main__":
    main()