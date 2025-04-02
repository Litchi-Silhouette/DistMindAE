import sys

def import_log(filename):
    log = []
    with open(filename) as f:
        f.readline()
        for line in f.readlines():
            parts = line.split(',')
            timestamp = parts[0].strip()
            index = parts[1].strip()
            utilization = float(parts[2].strip().strip('%'))
            log.append((timestamp, index, utilization))
    return log

def export_summary(filename, summary):
    with open(filename, 'w') as f:
        for timestamp, all_utilization in summary:
            all_utilization_str = [str(u) for u in all_utilization]
            f.write('%s, %s\n' % (timestamp, ', '.join(all_utilization_str)))

def main():
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    num_gpu = int(sys.argv[3])

    log = import_log(input_filename)
    num_snapshot = len(log) // num_gpu

    summary = []
    for i in range(num_snapshot):
        timestamp = log[i * num_gpu][0]

        all_utilization = []
        for j in range(num_gpu):
            _, _, utilization = log[i * num_gpu + j]
            all_utilization.append(utilization)

        summary.append((timestamp, all_utilization))

    export_summary(output_filename, summary)

if __name__ == "__main__":
    main()