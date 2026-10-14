import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import time
import traceback
import json
import numpy as np
from itertools import product
def dumps(file_name, data, i=None):
    if i != None:
        if i == 'Clean':
            if os.path.exists(file_name) == True:
                os.remove(file_name)
        else:
            file_name = os.path.join(i, file_name)
    try:
        if len(data) < 1:
            print('File is empty!:', file_name)
    except:
        pass
    with open(file_name, "w") as config:
        json.dump(data, config, indent=4)
def loads(file_name, i=None):
    io = {}
    if i != None:
        if os.path.exists(file_name) == False:
            dumps(file_name, io)
    try:
        if os.path.exists(file_name) == True:
            while True:
                try:
                    with open(file_name, "r") as file:
                        io = json.load(file)
                        time.sleep(.01)
                        break
                except IOError:
                    print("File Waiting:", file_name)
                    time.sleep(1)
    except Exception as e:
        print("Issues with:", file_name, e)
    return (io)
# Your data
try:
    data = loads('Ethernet_pairmode.json')
    data1 = {}
    broken_data = []
    for line in data:
        n = data.get(line)[2]
        if len(n) == 2 and len(n[0]) == 3 and len(n[1]) == 3:
            data1[line] = (data.get(line))
        else:
            broken_data.append(line)
        try:
            t = int(data.get(line)[2][1][1])
        except:
            print('Broken', line)
            broken_data.append(line)
    print('Broken Data:', len(broken_data))
    if len(broken_data) > 1:
        print(broken_data[0])
        confirm = input('Delete Broken Data From Pairmode? Y/N: ')
        if confirm.lower() == 'y':
            for line in broken_data:
                del data[line]
            dumps('Ethernet_pairmode.json', data)
    data = data1
    print(f"Using {len(data)} Data Sets")
    eth_x = [int(v[1]) for v in data.values()]
    eth_y = [v[2][0][2] for v in data.values()]
    wifi_x = [int(v[2][0][1]) for v in data.values()]
    hypo_x = [int(v[2][1][1]) for v in data.values()]
    hypo_graph = [[a, b] for a, b in zip(hypo_x, eth_y)]
    ethernet_max = max(eth_x)
    hypo_graph_paired = []
    for line in hypo_graph:
        if line[0] <= ethernet_max:
            hypo_graph_paired.append(line)
    hypo_graph_x, hypo_graph_y = zip(*hypo_graph_paired)

    #Graph 4 Smoothed

    iox = loads('Ethernet_avg.json')

    v1x = [int(v[1]) for v in iox.values()]
    v1y = [v[7] for v in iox.values()]
    print(len(v1y), len(v1x))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Network Adapter MTU Metrics', fontsize=14, fontweight='bold')
    #Hide the 4th Panel
    axes[1, 1].axis('on')

    # Helper: overlay a line graph across the bar
    def overlay_line(ax, value, color, label):
        x = np.linspace(-0.4, 0.4, 25)
        y = np.full_like(x, value, dtype=float)
        ax.plot(x, y, color=color, linewidth=2.5, marker='o', markersize=5, label=label)

    # --- Bar 1: Ethernet (0 - 9000) ---
    ax1 = axes[0, 0]
    #ax1.bar(eth_x, eth_y, color='steelblue', width=0.5, alpha=0.85)
    ax1.scatter(eth_x, eth_y, color='steelblue', alpha=0.85, s=30)
    #overlay_line(ax1, ethernet_val, 'navy', f'Ethernet = {ethernet_val}')
    ax1.set_xlim(min(eth_x), max(eth_x))
    #ax1.set_ylim(x_axis_min, x_axis_max)
    #ax1.set_xlabel('Value')
    ax1.set_title(f'Ethernet: Raw')
    #ax1.axhline(y=9000, color='red', linestyle='--', alpha=0.5, label='Max (9000)')
    #ax1.legend(loc='upper right')
    #ax1.grid(axis='x', alpha=0.3)

    # --- Bar 2: Wi-Fi (0 - 1500) ---
    ax2 = axes[0, 1]
    ax2.scatter(wifi_x, eth_y, color='saddlebrown', alpha=0.85, s=30)
    #ax2.bar([wifi_name], [wifi_val], color='darkorange', width=0.5, alpha=0.85)
    #overlay_line(ax2, wifi_val, 'saddlebrown', f'Wi-Fi = {wifi_val}')
    ax2.set_xlim(min(wifi_x), max(wifi_x))
    #ax2.set_ylabel('Value')
    ax2.set_title(f'Wi-Fi: Raw')
    #ax2.axhline(y=1500, color='red', linestyle='--', alpha=0.5, label='Max (1500)')
    #ax2.legend(loc='upper right')
    #ax2.grid(axis='y', alpha=0.3)

    # --- Bar 3: HypoMux-Tun (0 - 9000) ---
    ax3 = axes[1, 0]
    #ax3.bar([hypo_name], [hypo_val], color='seagreen', width=0.5, alpha=0.85)
    #overlay_line(ax3, hypo_val, 'darkgreen', f'HypoMux-Tun = {hypo_val}')
    ax3.scatter(hypo_graph_x, hypo_graph_y, color='darkgreen', alpha=0.85, s=30)
    ax3.set_xlim(min(hypo_graph_x), max(hypo_graph_x))
    #ax3.set_xticks(range(0, max(hypo_graph_paired), (max(hypo_x) // 9)))
    #ax3.set_ylabel('Value')
    ax3.set_title(f'HypoMux-Tun: Raw')
    #ax3.axhline(y=9000, color='red', linestyle='--', alpha=0.5, label='Max (9000)')
    #ax3.legend(loc='upper right')
    #ax3.grid(axis='y', alpha=0.3)

    # --- Bar 4: HypoMux-Tun (0 - 9000) ---
    ax4 = axes[1, 1]
    #ax3.bar([hypo_name], [hypo_val], color='seagreen', width=0.5, alpha=0.85)
    #overlay_line(ax3, hypo_val, 'darkgreen', f'HypoMux-Tun = {hypo_val}')
    ax4.scatter(v1x, v1y, color='purple', alpha=0.85, s=30)
    ax4.set_xlim(min(v1x), max(v1x))
    #ax3.set_ylabel('Value')
    ax4.set_title(f'Ethernet: Averaged')
    #ax4.axhline(y=9000, color='red', linestyle='--', alpha=0.5, label='Max (9000)')
    #ax4.legend(loc='upper right')
    #ax4.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    try:
        plt.savefig("plot.png", dpi=300, bbox_inches="tight")
    except:
        pass
    plt.show()
    input('Exit')
except Exception as e:
    print('Plot Issues:', e)
    traceback.print_exc()
    input('Exit')