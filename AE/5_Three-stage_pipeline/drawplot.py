#!/usr/bin/env python3

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from collections import defaultdict

# Define model full names
MODEL_NAMES = {
    'res': 'ResNet',
    'inc': 'Inception v3',
    'den': 'DenseNet',
    'bert': 'BERT',
    'gpt': 'GPT-2'
}

def get_batch_size_label(folder_name):
    """Convert folder name to appropriate batch size label"""
    if folder_name == '1':
        return 'per layer'
    elif folder_name == '536870912':  # This is the largest, assuming it's "per app"
        return 'per app'
    else:
        # Convert to MB
        size_bytes = int(folder_name)
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.0f} MB"

def extract_latencies(log_file):
    """Extract all latency values from a log file"""
    latencies = []
    try:
        with open(log_file, 'r') as f:
            content = f.read()
            # Find all latency values using regex
            matches = re.findall(r'Total Latency: (\d+\.\d+) ms', content)
            latencies = [float(match) for match in matches]
    except Exception as e:
        print(f"Error reading {log_file}: {e}")
    
    return latencies

def collect_data(base_dir):
    """Collect latency data from all test directories"""
    data = {}
    
    # Get all batch size directories
    batch_dirs = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])
    
    for batch_dir in batch_dirs:
        batch_path = os.path.join(base_dir, batch_dir)
        batch_label = get_batch_size_label(batch_dir)
        data[batch_label] = {}
        
        # Get all model type directories
        model_dirs = [d for d in os.listdir(batch_path) if os.path.isdir(os.path.join(batch_path, d))]
        
        for model_dir in model_dirs:
            model_path = os.path.join(batch_path, model_dir)
            
            # Find all worker log files
            worker_logs = glob(os.path.join(model_path, "log_worker_*.txt"))
            
            if not worker_logs:
                print(f"No worker logs found for {batch_label}/{model_dir}")
                continue
                
            # Extract latencies from all worker logs
            all_latencies = []
            for log in worker_logs:
                latencies = extract_latencies(log)
                all_latencies.extend(latencies)
            
            # Calculate average if we have any latencies
            if all_latencies:
                avg_latency = np.mean(all_latencies)
                data[batch_label][model_dir] = avg_latency
                print(f"Average latency for {batch_label}/{model_dir}: {avg_latency:.2f} ms")
            else:
                print(f"No latency data found for {batch_label}/{model_dir}")
    
    return data

# Keep the old function for backwards compatibility
def plot_data(data):
    """Create bar chart from collected data without bounds"""
    # Get all models and batch sizes
    all_models = sorted(list(set([model for batch_sizes in data.values() for model in batch_sizes.keys()])))
    batch_sizes = sorted(list(data.keys()))
    
    # Organize data for plotting
    plot_data = defaultdict(list)
    x_labels = []
    
    for model in all_models:
        x_labels.append(MODEL_NAMES.get(model, model))
        for batch in batch_sizes:
            plot_data[batch].append(data.get(batch, {}).get(model, 0))
    
    # Set up the bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Define width of bars and positions
    bar_width = 0.8 / len(batch_sizes)
    r = np.arange(len(x_labels))
    
    # Plot bars for each batch size
    for i, (batch, values) in enumerate(plot_data.items()):
        position = r + bar_width * i - (len(batch_sizes)-1) * bar_width / 2
        ax.bar(position, values, width=bar_width, label=batch)
    
    # Add labels and legend
    ax.set_xlabel('Model Type', fontweight='bold')
    ax.set_ylabel('Latency (ms)', fontweight='bold')
    ax.set_title('Model Latency by Batch Size', fontweight='bold')
    ax.set_xticks(r)
    ax.set_xticklabels(x_labels)
    ax.legend()
    
    # Add grid for better readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    
    # Save and show the plot
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'latency_comparison.png')
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")
    
    plt.close()

def collect_bound_data(base_dir):
    """Collect latency bound data from test1/gpu"""
    bound_data = {}
    
    # Get all model type directories
    model_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    for model_dir in model_dirs:
        model_path = os.path.join(base_dir, model_dir)
        
        # Find all worker log files
        worker_logs = glob(os.path.join(model_path, "log_worker_*.txt"))
        
        if not worker_logs:
            print(f"No worker logs found for bound/{model_dir}")
            continue
            
        # Extract latencies from all worker logs
        all_latencies = []
        for log in worker_logs:
            latencies = extract_latencies(log)
            all_latencies.extend(latencies)
        
        # Calculate average if we have any latencies
        if all_latencies:
            avg_latency = np.mean(all_latencies)
            bound_data[model_dir] = avg_latency
            print(f"GPU bound latency for {model_dir}: {avg_latency:.2f} ms")
        else:
            print(f"No bound latency data found for {model_dir}")
    
    return bound_data

def plot_data_with_bound(data, bound_data):
    """Create bar chart from collected data with bounds"""
    # Get all models and batch sizes
    all_models = sorted(list(set([model for batch_sizes in data.values() for model in batch_sizes.keys()])))
    batch_sizes = sorted(list(data.keys()))
    
    # Organize data for plotting
    plot_data = defaultdict(list)
    x_labels = []
    bounds = []
    
    for model in all_models:
        x_labels.append(MODEL_NAMES.get(model, model))
        bounds.append(bound_data.get(model, 0))
        for batch in batch_sizes:
            plot_data[batch].append(data.get(batch, {}).get(model, 0))
    
    # Set up the bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Define width of bars and positions
    bar_width = 0.8 / len(batch_sizes)
    r = np.arange(len(x_labels))
    
    # Plot bars for each batch size
    for i, (batch, values) in enumerate(plot_data.items()):
        position = r + bar_width * i - (len(batch_sizes)-1) * bar_width / 2
        ax.bar(position, values, width=bar_width, label=batch)
    
    # Plot bounds as short horizontal lines for each model
    if any(bounds):
        for i, (x, y) in enumerate(zip(r, bounds)):
            if y > 0:
                # Plot a short horizontal line for the bound
                line_width = 0.4  # Width of the horizontal line
                ax.plot([x - line_width/2, x + line_width/2], [y, y], 
                        'r-', linewidth=2.5, solid_capstyle='butt')
                
                # Add the value label above the line
                ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", 
                            xytext=(0,5), ha='center')
    
    # Add a small entry to the legend for the bound line
    ax.plot([], [], 'r-', linewidth=2.5, label='GPU Bound')
    
    # Add labels and legend
    ax.set_xlabel('Model Type', fontweight='bold')
    ax.set_ylabel('Latency (ms)', fontweight='bold')
    ax.set_title('Model Latency by Batch Size with GPU Bounds', fontweight='bold')
    ax.set_xticks(r)
    ax.set_xticklabels(x_labels)
    ax.legend()
    
    # Add grid for better readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    
    # Save and show the plot
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fig11_a.png')
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")
    
    plt.close()

def main():
    # Base directories for data
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                           'tmp/test5')
    bound_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                            'tmp/test1/gpu')
    
    # Collect main data
    print(f"Collecting latency data from {base_dir}")
    data = collect_data(base_dir)
    
    if not data:
        print("No data found. Exiting.")
        return
    
    # Collect bound data
    print(f"\nCollecting bound data from {bound_dir}")
    bound_data = collect_bound_data(bound_dir)
    
    # Plot with bounds
    plot_data_with_bound(data, bound_data)
    print("Latency analysis completed!")

if __name__ == "__main__":
    main()