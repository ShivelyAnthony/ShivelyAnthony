from multiprocessing import Pool
import glob
import json
import numpy as np
import os
import random
import time
import torch
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
def tasker():
    try:
        out = subprocess.check_output(["python", "cpu_task.py"], text=True)
        v1 = float(out.strip().splitlines()[0])
        return(v1)
    except Exception as e:
        print('Make sure cpu_task.py is in the same location.')
        print('If not you have to download it or create your own.')
        print('Tasker Issues', e)
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
def work(n):
    return sum(i * i for i in range(n))

def run():
    chunks = [250_000] * 8
    start = time.perf_counter()
    with Pool() as pool:
        results = pool.map(work, chunks)
    return time.perf_counter() - start

def work1(n, device):
    # Create array on device to avoid host->device transfer overhead
    x = torch.arange(n, dtype=torch.int64, device=device)
    return (x * x).sum().item()

def run1():
    chunks = [250_000] * 8

    # Auto-detect: ROCm exposes itself as 'cuda' in PyTorch
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Warm-up (first GPU call compiles kernels)
    work1(1000, device)
    if device == "cuda":
        torch.cuda.synchronize()

    start = time.perf_counter()
    results = [work1(n, device) for n in chunks]
    if device == "cuda":
        torch.cuda.synchronize()  # Wait for GPU to finish
    iox = loads('Test Save.json')
    frame = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
             'v', 'w']
    # frame2 = list(random.shuffle(frame))
    frame2 = random.sample(frame, len(frame))
    frame3 = random.sample(frame, len(frame))
    iop = []
    for line in frame:
        for line_x in frame2:
            iop.append(line_x)
            for line_z in frame3:
                iop.append(frame3)
    iox['Test Saving'] = (iop)
    dumps('Test Save.json', iox)
    v1 = time.perf_counter() - start
    return v1, results, device
if __name__ == "__main__":
    a = np.random.rand(128_128)
    start = time.perf_counter()
    b = a * 2
    #print(f"{(a.nbytes * 3) / (time.perf_counter() - start) / 1e9:.1f} GB/s")
    v1 = run()
    print(v1)
    v2, results, device = run1()
    print(v2 + v1)
    #input("Exit")