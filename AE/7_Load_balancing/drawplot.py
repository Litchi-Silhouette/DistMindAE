import os
import re
import matplotlib.pyplot as plt
import numpy as np
import sys

from py_utils.check_client import extract_last_block_metrics

# Directories containing log files
lb_lfu_dir = "./tmp/test7/lb_lfu"
load_balancer_dir = "./tmp/test7/load_balancer"

# Regular expression to extract zipf from file names
pattern = r"log_client_zipf([\d\.]+)_resched\d+\.txt"

# Dictionary to store data for both directories
data = {
    "lb_lfu": {},
    "load_balancer": {}
}

# Process log files from the lb_lfu directory
for filename in os.listdir(lb_lfu_dir):
    if filename.startswith("log_client"):
        match = re.match(pattern, filename)
        if match:
            zipf_value = float(match.group(1))
            
            # Get metrics from the log file
            log_path = os.path.join(lb_lfu_dir, filename)
            metrics = extract_last_block_metrics(log_path)
            
            if metrics and metrics["Average Throughput"] is not None:
                throughput = metrics["Average Throughput"]
                data["lb_lfu"][zipf_value] = throughput
                print(f"lb_lfu - File: {filename}, Zipf: {zipf_value}, Throughput: {throughput} rps")
            else:
                print(f"No metrics found in {filename}")

# Process log files from the load_balancer directory
for filename in os.listdir(load_balancer_dir):
    if filename.startswith("log_client"):
        match = re.match(pattern, filename)
        if match:
            zipf_value = float(match.group(1))
            
            # Get metrics from the log file
            log_path = os.path.join(load_balancer_dir, filename)
            metrics = extract_last_block_metrics(log_path)
            
            if metrics and metrics["Average Throughput"] is not None:
                throughput = metrics["Average Throughput"]
                data["load_balancer"][zipf_value] = throughput
                print(f"load_balancer - File: {filename}, Zipf: {zipf_value}, Throughput: {throughput} rps")
            else:
                print(f"No metrics found in {filename}")

# Create lists for plotting
zipf_values = sorted(set(list(data["lb_lfu"].keys()) + list(data["load_balancer"].keys())))
lb_lfu_throughputs = [data["lb_lfu"].get(zipf, 0) for zipf in zipf_values]
load_balancer_throughputs = [data["load_balancer"].get(zipf, 0) for zipf in zipf_values]

# Convert zipf values to string labels for x-axis
zipf_labels = [str(zipf) for zipf in zipf_values]

# Plot the bar chart
plt.figure(figsize=(12, 7))

# Set width of bars
bar_width = 0.35
index = np.arange(len(zipf_values))

# Plot bars
lb_lfu_bars = plt.bar(index - bar_width/2, lb_lfu_throughputs, bar_width, 
                      color='#3498db', label='Least')
load_balancer_bars = plt.bar(index + bar_width/2, load_balancer_throughputs, bar_width, 
                            color='#e74c3c', label='DistMind')

# Parse GPU bound from the log file
gpu_log_path = "./tmp/test2/gpu/log_client_zipf0.9_resched1.txt"
gpu_metrics = extract_last_block_metrics(gpu_log_path)
if gpu_metrics and gpu_metrics["Average Throughput"] is not None:
    gpu_bound = gpu_metrics["Average Throughput"]
    print(f"GPU Bound Throughput: {gpu_bound} rps")
else:
    # Fallback in case parsing fails
    gpu_bound = 60
    print(f"Could not parse GPU bound, using default: {gpu_bound} rps")

# Add reference line for GPU bound
plt.axhline(y=gpu_bound, color='green', linestyle='--', linewidth=2, label=f'GPU Bound ({gpu_bound} rps)')

# Customize plot
plt.xlabel('Zipf Value', fontsize=14)
plt.ylabel('Throughput (rps)', fontsize=14)
plt.title('fig12_a: Load Balancer', fontsize=16)
plt.xticks(index, zipf_labels)
plt.legend(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Adjust layout and save the plot
plt.tight_layout()

output_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(output_dir, 'fig12_a.png'), dpi=300, bbox_inches='tight')
print("Plot saved")
