import os
import re
import matplotlib.pyplot as plt
import numpy as np
from py_utils.check_client import extract_last_block_metrics

# Directory containing log files
log_dir = "./tmp/test8"

# Regular expression to extract cache_size and resched from file names
pattern = r"log_client_cache_size(\d+)_resched([\d\.]+)\.txt"

# Dictionary to store data: {cache_size: {resched: throughput}}
data = {}

# Process all log files
for filename in os.listdir(log_dir):
    if filename.startswith("log_client"):
        match = re.match(pattern, filename)
        if match:
            cache_size_bytes = int(match.group(1))
            resched_value = float(match.group(2))
            
            # Convert cache_size to GB
            cache_size_gb = cache_size_bytes / 1024000000
            
            # Convert resched to ms
            resched_ms = resched_value * 1000
            
            # Get metrics from the log file
            log_path = os.path.join(log_dir, filename)
            metrics = extract_last_block_metrics(log_path)
            
            if metrics and metrics["Average Throughput"] is not None:
                throughput = metrics["Average Throughput"]
                
                # Initialize nested dictionary if needed
                if cache_size_gb not in data:
                    data[cache_size_gb] = {}
                
                # Store throughput data
                data[cache_size_gb][resched_ms] = throughput
                print(f"File: {filename}, Cache: {cache_size_gb:.2f}GB, Resched: {resched_ms:.1f}ms, Throughput: {throughput} rps")
            else:
                print(f"No metrics found in {filename}")

# Plot the data
plt.figure(figsize=(10, 6))

# Define colors and markers for different cache sizes
colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
markers = ['o', 's', '^', 'D', 'x', '*']

# Sort cache sizes for consistent colors in the legend
cache_sizes = sorted(data.keys())

for i, cache_size in enumerate(cache_sizes):
    # Sort resched values for x-axis
    resched_values = sorted(data[cache_size].keys())
    throughputs = [data[cache_size][r] for r in resched_values]
    
    color = colors[i % len(colors)]
    marker = markers[i % len(markers)]
    
    plt.plot(resched_values, throughputs, 
             marker=marker, linestyle='-', 
             linewidth=2, markersize=8, 
             color=color, 
             label=f'Cache Size: {cache_size:.2f} GB')

plt.xlabel('Resched Time (ms)', fontsize=12)
plt.ylabel('Throughput (rps)', fontsize=12)
plt.title('Fig12.b Caching', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

output_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(output_dir, exist_ok=True)
# Save the plot
plt.savefig(os.path.join(output_dir, 'fig12_b.png'), dpi=300, bbox_inches='tight')
print("Plot saved")
