from matplotlib import pyplot as plt
import numpy as np
import os

fig, ax = plt.subplots()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
fig.set_size_inches(6, 3)

data_dir = "./6_Zero-copy_deserialization/eval_results.txt"
output_dir = "./6_Zero-copy_deserialization/fig11b.png"

models = []
deserialize_full_model = []
deserialize_stripped_model = []
deserialize_func_list = []

with open(data_dir, "r") as f:
    lines = f.readlines()
    for line in lines:
        words = line.split()
        models.append(words[0])
        deserialize_full_model.append(float(words[5])*1000)
        deserialize_stripped_model.append(float(words[10])*1000)
        deserialize_func_list.append(float(words[15])*1000)

x = np.arange(len(models))
width = 0.15
plt.bar(x - width, deserialize_full_model, width, label='Pickle', color='g')
plt.bar(x, deserialize_stripped_model, width, label='Pickle+', color='orange')
plt.bar(x + width, deserialize_func_list, width, label='DistMind', color='b')

plt.xlabel('Model')
plt.ylabel('Latency (ms)')
plt.xticks(x, models, rotation=15)
plt.yscale('log', subs=[])
plt.ylim(0.1, 1000)

plt.margins(0.2)
plt.legend(loc='upper center', ncol=4, shadow=False, frameon=False)
plt.title('Fig11b. Deserializing overhead for different methods.')
plt.savefig(output_dir, bbox_inches='tight')
