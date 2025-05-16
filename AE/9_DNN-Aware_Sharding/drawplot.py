#!/usr/bin/env python3
"""
Draw plots from controller log data for DNN-Aware Sharding experiments.
This script reads the log_controller.txt file, parses the latency data 
from different experiments and generates comparison plots.
"""

import re
import os
import numpy as np
import matplotlib.pyplot as plt

# Path to the log file
LOG_FILE = './tmp/test9/log_controller.txt'

def read_log_file(file_path):
    """
    Read the log file and return its content
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Log file not found at {file_path}")
    
    with open(file_path, 'r') as f:
        return f.read()

def parse_hybrid_exp_data(log_content):
    """
    Parse hybrid_exp data from log content
    Returns a dictionary with batch numbers as keys and latency values as values
    """
    hybrid_data = {}
    
    # Regular expression to find hybrid_exp batch averages
    pattern = r'\[info\] hybrid_exp::batch (\d+) takes \(ms\)\[avg, min, max\]: ([0-9.]+)'
    matches = re.findall(pattern, log_content)
    
    # Group by batch number
    for batch, latency in matches:
        batch_num = int(batch)
        if batch_num not in hybrid_data:
            hybrid_data[batch_num] = []
        hybrid_data[batch_num].append(float(latency))
    
    return hybrid_data

def parse_hori_exp_data(log_content):
    """
    Parse hori_exp data from log content
    Returns a dictionary with batch numbers as keys and latency values as values
    """
    hori_data = {}
    
    # Regular expression to find hori_exp batch averages
    pattern = r'\[info\] hori_exp::batch (\d+) cost \(ms\)\[avg, min, max\]: ([0-9.]+)'
    matches = re.findall(pattern, log_content)
    
    # Group by batch number
    for batch, latency in matches:
        batch_num = int(batch)
        if batch_num not in hori_data:
            hori_data[batch_num] = []
        hori_data[batch_num].append(float(latency))
    
    return hori_data

def parse_verti_exp_data(log_content):
    """
    Parse verti_exp data from log content
    Returns a list of latency values
    """
    verti_data = {}
    
    # Regular expression to find verti_exp averages
    pattern = r'\[info\] verti_exp:: takes \(ms\)\[avg, min, max\]: ([0-9.]+)'
    matches = re.findall(pattern, log_content)
    
    # For verti_exp, we'll use group 0 for all values
    verti_data[0] = [float(latency) for latency in matches]
    
    return verti_data

def parse_per_app_exp_data(log_content):
    """
    Parse per_app_exp data from log content
    Returns a dictionary with group index 0 and latency values
    """
    per_app_data = {}
    
    # Regular expression to find per_app_exp averages
    pattern = r'\[info\] per_app_exp:: average \(ms\)\[avg, min, max\]: ([0-9.]+)'
    matches = re.findall(pattern, log_content)
    
    # For per_app_exp, we'll use group 0 for all values
    per_app_data[0] = [float(latency) for latency in matches]
    
    return per_app_data

def plot_experiment_comparison(hybrid_data, hori_data, verti_data, per_app_data, output_file='experiment_comparison.png'):
    """
    Create a line plot comparing all experiments with group index on x-axis and latency on y-axis
    """
    plt.figure(figsize=(14, 8))
    
    # Set line styles
    styles = {
        'hybrid_exp': {'color': 'blue', 'marker': 'o', 'label': 'hybrid_exp'},
        'hori_exp': {'color': 'orange', 'marker': 's', 'label': 'hori_exp'},
        'verti_exp': {'color': 'green', 'marker': '^', 'label': 'verti_exp'},
        'per_app_exp': {'color': 'red', 'marker': 'D', 'label': 'per_app_exp'}
    }
    
    # Hybrid experiment data
    hybrid_x = sorted(hybrid_data.keys())
    hybrid_y = [np.mean(hybrid_data[batch]) for batch in hybrid_x if len(hybrid_data[batch]) > 0]
    if hybrid_x and hybrid_y:
        plt.plot(hybrid_x, hybrid_y, marker=styles['hybrid_exp']['marker'], linestyle='-', 
                 color=styles['hybrid_exp']['color'], label=styles['hybrid_exp']['label'], 
                 linewidth=2, markersize=10)
    
    # Horizontal experiment data
    hori_x = sorted(hori_data.keys())
    hori_y = [np.mean(hori_data[batch]) for batch in hori_x if len(hori_data[batch]) > 0]
    if hori_x and hori_y:
        plt.plot(hori_x, hori_y, marker=styles['hori_exp']['marker'], linestyle='-',
                 color=styles['hori_exp']['color'], label=styles['hori_exp']['label'], 
                 linewidth=2, markersize=10)
    
    # Vertical experiment data
    for group in sorted(verti_data.keys()):
        if len(verti_data[group]) > 0:
            verti_avg = np.mean(verti_data[group])
            
            # For verti_exp, use the same y value for all x points (0-7)
            x_points = list(range(8))  # 0-7 for the 7 batches
            y_points = [verti_avg] * len(x_points)
            plt.plot(x_points, y_points, marker=styles['verti_exp']['marker'], linestyle='-',
                     color=styles['verti_exp']['color'], label=styles['verti_exp']['label'], 
                     linewidth=2, markersize=10)
    
    # Per-app experiment data
    for group in sorted(per_app_data.keys()):
        if len(per_app_data[group]) > 0:
            per_app_avg = np.mean(per_app_data[group])
            
            # For per_app_exp, use the same y value for all x points (0-7)
            x_points = list(range(8))  # 0-7 for the 7 batches
            y_points = [per_app_avg] * len(x_points)
            plt.plot(x_points, y_points, marker=styles['per_app_exp']['marker'], linestyle='-',
                     color=styles['per_app_exp']['color'], label=styles['per_app_exp']['label'], 
                     linewidth=2, markersize=10)
    
    plt.xlabel('Group Index', fontsize=14)
    plt.ylabel('Latency (ms)', fontsize=14)
    plt.title('Fig. 13. Latency for different sharding methods.', fontsize=16)
    plt.grid(True)
    
    # Only show one legend entry per experiment type
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='best')
    
    # Set x-axis to integers
    plt.xticks(range(8))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Saved experiment comparison plot to {output_file}")

def main():
    """Main function to run the script"""
    try:
        # Read log file
        log_content = read_log_file(LOG_FILE)
        
        # Parse data
        hybrid_data = parse_hybrid_exp_data(log_content)
        hori_data = parse_hori_exp_data(log_content)
        verti_data = parse_verti_exp_data(log_content)
        per_app_data = parse_per_app_exp_data(log_content)
        
        print("Parsed data successfully")
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(os.path.abspath(__file__))
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate main experiment comparison plot
        plot_experiment_comparison(hybrid_data, hori_data, verti_data, per_app_data,
                                  os.path.join(output_dir, 'fig13.png'))
        
        print("All plots have been generated successfully")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
