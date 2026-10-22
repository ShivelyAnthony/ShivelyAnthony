'''

2026 - MTU Adjuster Developed by Anthony R. Shively (Mercer, Ohio 1997)
Attribution Notice: If this software, its source code, or its documentation is used in machine-learning training, AI development, research, or related applications,
please acknowledge the original source and credit me, Anthony R. Shively as the software's developer. Thank you, have a great day.

'''

#Get-NetIPInterface | Format-Table InterfaceAlias,AddressFamily,NlMtu,ConnectionState
#Set-NetIPInterface -InterfaceAlias "Wi-Fi" -AddressFamily IPv4 -NlMtuBytes 800
import subprocess
import ctypes
import random
import json
import os
import glob
import time
import psutil
import speedtest
import socket
import re
import traceback
import segno
from ctypes import wintypes
import statistics
import pyautogui
import gc
from scapy.all import rdpcap, raw
import pyshark
#from icmplib import ping
from concurrent.futures import ThreadPoolExecutor, as_completed
from icmplib import ping as pingx
from multiprocessing import Pool
import torch
import numpy as np
from PyLibreHardwareMonitor import Computer
#from rich.progress import track
import math
import requests
def curl_to_python(url, headers=None, data=None):
    time_manage = (url + " Time")
    url_m = (url + " Last State")
    now_time = float(time.time())
    io = loads('Url Manager.json')
    iov = {}
    if url in io:
        iov = io.get(url)
    time_get = 0
    time_sleep = 0.5
    if time_manage in iov and url_m in iov:
        time_get = float(iov.get(time_manage))
        if iov.get(url_m) == "Bad":
            time_get = (time_get + 1800)
            time_sleep = 1
    if headers == None:
        headers = {"Content-Type": "application/json"}
    # Get and Post are Different Here!!
    # 60 is changed for this program but should be atleast 300 (5 Mins) to bypass being rate limited
    if (float(time_get + 30)) < float(now_time):
        time.sleep(time_sleep)
        if data == None:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print("Bad Get Url:",  url)
                iov[time_manage] = (now_time)
                iov[url_m] = ("Bad")
                io[url] = (iov)
                dumps('Url Manager.json', io)
            elif response.status_code == 200 or response.status_code == "200":
                iov[url] = (response.json())
                iov[time_manage] = (now_time)
                iov[url_m] = ("Good")
                io[url] = (iov)
                dumps("Url Manager.json", io)
            return(response.json())
        else:
            time.sleep(.25)
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code != 200:
                print("Bad Post Url:",  url)
            return(response.json())
    else:
        if url in iov:
            z = iov.get(url)
            return(z)
def terra():
    try:
        io = loads('Simple Terra Exchange.json')
        try:
            url = 'https://terra-classic-lcd.publicnode.com/terra/oracle/v1beta1/denoms/exchange_rates'
            data = curl_to_python(url)
            x = data['exchange_rates']
            for line in x:
                io[line['denom']] = (float(line['amount']))
            dumps('Simple Terra Exchange.json', io)
        except:
            print('Terra Exchange Rates Down')
            traceback.print_exc()
    except Exception as e:
        print('Terra Issues:', e)
def terra_weight():
    try:
        io = loads(f"Simple Terra Exchange.json")
        terra_list = []
        for line in io:
            terra_list.append(io.get(line))
        terra_avg = (1 / (min(terra_list) / (sum(terra_list) / len(terra_list))))
        #terra_avg = (sum(terra_list) / len(terra_list))
        #return(((1 + abs(1 - terra_avg)) / 1))
        return(terra_avg)
    except Exception as e:
        print('Terra Weight Issues:', e)
        return(1)
def sqrt(a, b=None):
    try:
        if b == None:
            #b = a
            z = math.sqrt(a)
            return(z)
        else:
            c = (a + b)
            d = (a * b)
            e = (d / c)
            f = (e * 2)
            return(f)
    except Exception as e:
        print('Sqrt Issues:', e)
def ratio(a, b, i=None):
    if a == 0 or b == 0:
        return(0)
    if i == None:
        u = [a, b]
        price = (min(u) / max(u))
        return(price)
    else:
        u = [a, b]
        price = (max(u) / min(u))
        return(price)
class PERFORMANCE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('CommitTotal', ctypes.c_size_t),
        ('CommitLimit', ctypes.c_size_t),
        ('CommitPeak', ctypes.c_size_t),
        ('PhysicalTotal', ctypes.c_size_t),
        ('PhysicalAvailable', ctypes.c_size_t),
        ('SystemCache', ctypes.c_size_t),
        ('KernelTotal', ctypes.c_size_t),
        ('KernelPaged', ctypes.c_size_t),      # Paged Pool (in pages)
        ('KernelNonpaged', ctypes.c_size_t),   # Non-paged pool (in pages)
        ('PageSize', ctypes.c_size_t),         # Page size in bytes
        ('HandleCount', wintypes.DWORD),
        ('ProcessCount', wintypes.DWORD),
        ('ThreadCount', wintypes.DWORD),
    ]
def get_performance_info() -> PERFORMANCE_INFORMATION:
    """Populate and return a PERFORMANCE_INFORMATION structure."""
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    info = PERFORMANCE_INFORMATION()
    info.cb = ctypes.sizeof(info)
    if not psapi.GetPerformanceInfo(ctypes.byref(info), info.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return info
def cpu_ram_gpu():
    try:
        info = get_performance_info()
        ram = psutil.virtual_memory()
        computer = Computer()
        #print(computer)
        #print(computer.network)
        #print(computer.gpu)
        v2 = computer.memory
        temps = []
        try:
            v1 = computer.cpu
            for line in v1:
                cpu_temps = []
                cpu1 = v1.get(line).get('Load')
                cpu_temps1 = []
                for line_x in cpu1:
                    cpu_temps1.append(cpu1.get(line_x))
                cpu_temps.append(sum(cpu_temps1) / len(cpu_temps1))
                cpu_temps2 = []
                cpu2 = v1.get(line).get('Power')
                for line_x in cpu2:
                    cpu_temps2.append(cpu2.get(line_x))
                cpu_temps.append(sum(cpu_temps2) / len(cpu_temps2))
                cpu3 = v1.get(line).get('Temperature').get('Core (Tctl/Tdie)')
                cpu_temps.append(cpu3)
                temps.append((sum(cpu_temps) / len(cpu_temps)))
        except Exception as e:
            print('CPU Issues:', e)
        try:
            v2 = computer.memory
            for line in v2:
                try:
                    mem1 = float(v2.get(line).get('Load').get('Memory'))
                    mem2 = float(v2.get(line).get('Load').get('Virtual Memory'))
                    mem_load = [mem1, mem2]
                    mem_avg = (sum(mem_load) / len(mem_load))
                    temps.append(mem_avg)
                except Exception as e:
                    print('Memory Issues:', e)
        except Exception as e:
            print('MEM Issues:', e)
        try:
            v3 = computer.gpu
            for line in v3:
                try:
                    gpu_core_temp = v3.get(line).get('Temperature').get('GPU Core')
                    gpu_power = v3.get(line).get('Power').get('GPU Package')
                    gpu_temps = [gpu_core_temp, gpu_power]
                    avg_gpu_temp_loads = (sum(gpu_temps) / len(gpu_temps))
                    temps.append(avg_gpu_temp_loads)
                except Exception as e:
                    print('GPU Issues:', e)
        except Exception as e:
            print('GPU Issues:', e)
        load1 = ((sum(temps) / len(temps)) / 100)
        load2 = (ram.percent / 100)
        load_list = [load1, load2]
        '''page_fields = [
        ('Commit Total',      info.CommitTotal),
        ('Commit Limit',      info.CommitLimit),
        ('Commit Peak',       info.CommitPeak),
        ('Physical Total',    info.PhysicalTotal),
        ('Physical Available', info.PhysicalAvailable),
        ('System Cache',      info.SystemCache),
        ('Kernel Total',      info.KernelTotal),
        ('Paged Pool',        info.KernelPaged),
        ('Non-Paged Pool',    info.KernelNonpaged),
        ]'''
        '''hynix = sym('hynix')
        equation = Eq(hynix, ())
        solution = solve(equation, hynix)
        print(float(solution[0]))'''
        load_list.append(ratio(info.CommitLimit, (info.PhysicalTotal * 2)))
        load_list.append(ratio(info.CommitLimit, (info.PhysicalTotal * 2)))
        load_list.append(ratio(info.CommitLimit, (info.PhysicalTotal * 2)))
        load_list.append(ratio(info.CommitLimit, (info.PhysicalTotal * 2)))
        ram_list = [info.KernelPaged, info.KernelTotal, info.SystemCache, info.KernelNonpaged]
        avgx= ratio((sum(ram_list) / len(ram_list)), sqrt(min(ram_list), max(ram_list)))
        load_list.append(avgx)
        #print(load_list)
        avg_sqrt = (min(load_list) / max(load_list))
        return(avg_sqrt)
    except Exception as e:
        print('CPU RAM GPU Issues:', e)
def response_timing():
    try:
        results = []
        for _ in range(100):
            start = time.perf_counter_ns()
            pyautogui.press("a")
            end = time.perf_counter_ns()
            results.append((end - start) / 1_000_000)
        return((1 / (min(results) / max(results))))
    except Exception as e:
        print('Response Timing Issues:', e)
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
def tasker():
    try:
        out = subprocess.check_output(["python", "cpu_task.py"], text=True)
        v1 = float(out.strip().splitlines()[0])
        return(v1)
    except Exception as e:
        print('Make sure cpu_task.py is in the same location.')
        print('If not you have to download it or create your own.')
        print('Tasker Issues', e)
def get_temps():
    try:
        temps = []
        load = []
        v6_spec = 1
        computer = Computer()
        #print('')
        try:
            v1 = computer.cpu
            #print(v1)
            for line in v1:
                cpu_temps = []
                cpu1 = v1.get(line).get('Load')
                cpu_temps1 = []
                for line_x in cpu1:
                    cpu_temps1.append(cpu1.get(line_x))
                cpu_temps.append(sum(cpu_temps1) / len(cpu_temps1))
                cpu_temps2 = []
                cpu2 = v1.get(line).get('Power')
                for line_x in cpu2:
                    cpu_temps2.append(cpu2.get(line_x))
                cpu_temps.append(sum(cpu_temps2) / len(cpu_temps2))
                cpu3 = v1.get(line).get('Temperature').get('Core (Tctl/Tdie)')
                cpu_temps.append(cpu3)
                tasking = tasker()
                if tasking < min(cpu_temps) and tasking > 0:
                    while tasking < min(cpu_temps):
                        tasking = (tasking * 10)
                elif tasking == 0:
                    print('Tasking is 0')
                cpu_temps.append(tasking)
                temps.append((sum(cpu_temps) / len(cpu_temps)))
        except Exception as e:
            print('CPU Issues:', e)
        #print('')
        try:
            v2 = computer.memory
            #print(v2)
            for line in v2:
                try:
                    mem1 = float(v2.get(line).get('Load').get('Memory'))
                    mem2 = float(v2.get(line).get('Load').get('Virtual Memory'))
                    mem_load = [mem1, mem2]
                    mem_avg = (sum(mem_load) / len(mem_load))
                    temps.append(mem_avg)
                except Exception as e:
                    print('Memory Issues:', e)
        except Exception as e:
            print('MEM Issues:', e)
        #print('')
        try:
            v3 = computer.gpu
            #print(v3)
            for line in v3:
                try:
                    gpu_core_temp = v3.get(line).get('Temperature').get('GPU Core')
                    gpu_power = v3.get(line).get('Power').get('GPU Package')
                    gpu_temps = [gpu_core_temp, gpu_power]
                    avg_gpu_temp_loads = (sum(gpu_temps) / len(gpu_temps))
                    temps.append(avg_gpu_temp_loads)
                except Exception as e:
                    print('GPU Issues:', e)
        except Exception as e:
            print('GPU Issues:', e)
        #print('')
        try:
            v4 = computer.motherboard
        except Exception as e:
            print('Motherboard Issues:', e)
        #print('')
        try:
            v5 = computer.controller
        except Exception as e:
            print('Controller Issues:', e)
        #print('')
        try:
            v6 = computer.network
            v6_d = []
            v6_u = []
            for line in v6:
                v6_d.append(v6.get(line).get('Throughput').get('Download Speed'))
                v6_u.append(v6.get(line).get('Throughput').get('Upload Speed'))
            v6_d.sort(reverse=True)
            v6_u.sort(reverse=True)
            v6_list = [((sum(v6_d) + v6_d[1]) / 2), ((sum(v6_u) + v6_u[1]) / 2)]
            v6_spec = (min(v6_list) / max(v6_list))
        except Exception as e:
            print('Network Issues:', e)
        #print('')
        try:
            v7 = computer.storage
            #print(v7)
            for line in v7:
                try:
                    single_temp = []
                    all_temp = v7.get(line).get('Temperature')
                    #print(all_temp)
                    for line_x in all_temp:
                        single_temp.append(int(all_temp.get(line_x)))
                    temps.append(sum(single_temp) / len(single_temp))
                except Exception as e:
                    pass
        except Exception as e:
            print('Storage Issues:', e)
        temps.append((min(temps) / v6_spec))
        avg_temp = (sum(temps) / len(temps))
        return(temps, avg_temp)
    except Exception as e:
        print('Get Temps Issues:', e)
def scoring_output(name, ipv):
    try:
        #iox[tn] = ([name, mtu, download, upload, ping, score])
        iox = loads(f"{name}.json")
        ioz = iox
        iox_t = {}
        all_mtus = [values[1] for values in iox.values()]
        mtus = set([values[1] for values in iox.values()])
        for line in mtus:
            o_download = []
            o_upload = []
            o_ping = []
            o_score = []
            o_temp = []
            o_temp_score = []
            for line_x in iox:
                if line == iox.get(line_x)[1]:
                    o_download.append(iox.get(line_x)[2])
                    o_upload.append(iox.get(line_x)[3])
                    o_ping.append(iox.get(line_x)[4])
                    o_score.append(iox.get(line_x)[5])
                    o_temp.append(iox.get(line_x)[6])
                    o_temp_score.append(iox.get(line_x)[7])
            iox_t[time.time()] = ([name, line, (sum(o_download) / len(o_download)), (sum(o_upload) / len(o_upload)), (sum(o_ping) / len(o_ping)), (sum(o_score) / len(o_score)), (sum(o_temp) / len(o_temp)), (sum(o_temp_score) / len(o_temp_score))])
        iox = iox_t
        '''iox_7 = ([values[7] for values in iox.values()]).sort(reverse=True)
        iox_t = {}
        for line in iox_7:
            for line_x in iox:
                if line == iox.get(line_x)[7]:
                    iox_t[line_x] = (iox.get(line_x))
        iox = iox_t'''
        dumps(f"{name}_avg.json", iox)
        download_scores = [values[2] for values in iox.values()]
        upload_scores = [values[3] for values in iox.values()]
        ping_scores = [values[4] for values in iox.values()]
        scores = [values[5] for values in iox.values()]
        load_temp = [values[6] for values in iox.values()]
        load_temp_score = [values[7] for values in iox.values()]
        max_download = max(download_scores)
        max_upload = max(upload_scores)
        min_ping = min(ping_scores)
        max_score = max(scores)
        min_load_temp = min(load_temp)
        max_load_temp_score = max(load_temp_score)
        for line in iox:
            if max_score == iox.get(line)[5]:
                score_index = iox.get(line)
            if min_ping == iox.get(line)[4]:
                ping_index = iox.get(line)
            if max_upload == iox.get(line)[3]:
                upload_index = iox.get(line)
            if max_download == iox.get(line)[2]:
                download_index = iox.get(line)
            if min_load_temp == iox.get(line)[6]:
                load_temp_index = iox.get(line)
            if max_load_temp_score == iox.get(line)[7]:
                load_temp_score_index = iox.get(line)
        ior = loads(f"{name}_output.json")
        ior['Max Download'] = ([download_index[0], download_index[1], download_index[2], download_index[3], download_index[4], download_index[5], int(download_index[6]), download_index[7], all_mtus.count(download_index[1])])
        ior['Max Upload'] = ([upload_index[0], upload_index[1], upload_index[2], upload_index[3], upload_index[4], upload_index[5], int(upload_index[6]), upload_index[7], all_mtus.count(upload_index[1])])
        ior['Lowest Ping'] = ([ping_index[0], ping_index[1], ping_index[2], ping_index[3], ping_index[4], ping_index[5], int(ping_index[6]), ping_index[7], all_mtus.count(ping_index[1])])
        ior['Max MTU Score'] = ([score_index[0], score_index[1], score_index[2], score_index[3], score_index[4], score_index[5], int(score_index[6]), score_index[7], all_mtus.count(score_index[1])])
        ior['Min Load Temp'] = ([load_temp_index[0], load_temp_index[1], load_temp_index[2], load_temp_index[3], load_temp_index[4], load_temp_index[5], int(load_temp_index[6]), load_temp_index[7], all_mtus.count(load_temp_index[1])])
        ior['Max Load Temp Score'] = ([load_temp_score_index[0], load_temp_score_index[1], load_temp_score_index[2], load_temp_score_index[3], load_temp_score_index[4], load_temp_score_index[5], int(load_temp_score_index[6]), load_temp_score_index[7], all_mtus.count(load_temp_index[1])])
        dumps(f"{name}_output.json", ior)
        ran_pick = [ping_index[1], score_index[1], upload_index[1], download_index[1], load_temp_index[1], load_temp_score_index[1]]
        '''if all_mtus.count(load_temp_score_index[1]) > 50:
            iop = change_mtu(name, ipv, load_temp_score_index[1])
            input('Program Finished: ', name, load_temp_score_index[1])'''
        #quick_pick = random.choice(ran_pick)
        #return(quick_pick)
    except Exception as e:
        print('Scoring Output Issues: ', e)
        traceback.print_exc()
def speed_tester(name, mtu):
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = float(st.download() / 1_000_000)
        upload = float(st.upload() / 1_000_000)
        ping = float(st.results.ping)
        if ping > 5000:
            ping = 5000
        elif ping == 0:
            ping = 1
        #x, y = scoring(name, mtu, download, upload, ping)
        #print('Speed Tester should be working')
        iox = loads(f"{name}.json")
        # Best Timing is towards 0 or 1, Remember to adjust Score based on divison.
        terra()
        extra_tests = [lan_scan(), terra_weight()] # response_timing() cpu_ram_gpu()
        avg_test = (sum(extra_tests) / len(extra_tests))
        score = (((download * .5) + (upload * .5)) / ((ping) * avg_test))
        tn = str(time.time())
        g1, g2 = get_temps()
        g2_score = (score / g2)
        iox[tn] = ([name, mtu, download, upload, ping, score, g2, g2_score])
        dumps(f"{name}.json", iox)
        return (1, tn, g2_score)
        #return (1, x, y)
    except Exception as e:
        # return(0, 0, 0, 0)
        # print('Speed Tester Issues:', e)
        return (0, 0, 0)
def get_mtu(name, ipv):
    try:
        command = (
            f'Get-NetIPInterface -InterfaceAlias "{name}" ' f'-AddressFamily {ipv} | ' 'Select-Object -ExpandProperty NlMtu')
        #command = ["powershell.exe", "-NoProfile", "-Command", f'Get-NetIPInterface -InterfaceAlias "{name}" ' f'-AddressFamily {ipv} | Select-Object -ExpandProperty NlMtuBytes']
        #print(command)
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, text=True)
        value = result.stdout.strip()
        return(value)
    except Exception as e:
        print('Get MTU Issues: ', e)
        return(0)
def change_mtu(name, ipv, mtu):
    try:
        command = (f'Set-NetIPInterface -InterfaceAlias "{name}" ' f'-AddressFamily IPV6 -NlMtuBytes {mtu}')
        # command = ["powershell.exe", "-NoProfile", "-Command", f'Set-NetIPInterface -InterfaceAlias "{name}" ' f'-AddressFamily {ipv} -NlMtuBytes {mtu}']
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, text=True)
        command = (f'Set-NetIPInterface -InterfaceAlias "{name}" ' f'-AddressFamily {ipv} -NlMtuBytes {mtu}')
        #command = ["powershell.exe", "-NoProfile", "-Command", f'Set-NetIPInterface -InterfaceAlias "{name}" ' f'-AddressFamily {ipv} -NlMtuBytes {mtu}']
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, text=True)
        #print(result)
        b = get_mtu(name, ipv)
        time.sleep(2)
        return(b)
    except Exception as e:
        print('Changing MTU Issues:', e)
def no_internet_boot():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(hostname,':', local_ip)
        print('')
        print('RFC 793 Transmission Control Protocol')
        print('######## TCP ########')
        conns = psutil.net_connections(kind="tcp")
        states = {}
        for c in conns:
            states[c.status] = states.get(c.status, 0) + 1
        for state, count in sorted(states.items()):
            print(f"{state}: {count}")
        print('')
        ioy = {}
        print('Ipv4 => Subnet => Router & DNS => ISP/Internet => DNS => Ipv4/Ipv6 => Server')
        testing = ['google.com', '192.168.1.1', '8.8.8.8', '4.4.4.4']
        print('Testing...')
        for line in testing:
            try:
                #print(f'Testing {line} Send SYN => Recieves SYN-ACK => Sends ACK')
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((line, 80))
                ioy[line] = ('Connected')
                client.close()
            except Exception as e:
                #print('Socket Issues:', e)
                ioy[line] = ('Disconnected')
        try:
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
            dns_servers = []
            for match in re.finditer(r"DNS Servers[.\s:]+([0-9a-fA-F:.]+)", result.stdout):
                dns_servers.append(match.group(1).strip())
            print('DNS Server Using:', dns_servers)
        except Exception as e:
            print('DNS Testing Issues:', e)
        for line in ioy:
            print(line, ioy.get(line))
        print('')
    except Exception as e:
        print('No Internet Boot Issues: ', e)
def pair_mode_settings(name, mtu, ipv, stamp, devices, u=None):
    try:
        #Name = Wifi
        #MTU = 1500
        #IPV = IPV4
        #Stamp = time.time()
        #Devices = ['Hypomux', 'Wifi']
        #U = time.time() from Best Plot
        iox = loads(f"{name}.json")
        iox_pair = loads(f"{name}_pairmode.json")
        trio = loads(f"{name}_trio.json")
        if 1 == 1:
            trio_list = [name, mtu]
            #Record MTU Devices
            device_record = []
            for line_a in devices:
                device_mtu = get_mtu(line_a, ipv)
                device_record.append([line_a, device_mtu, iox.get(stamp)[7]])
                trio_list.append(line_a)
                trio_list.append(device_mtu)
            trio_list.append(iox.get(stamp)[7])
            rto1, rto2 = rto_check()
            iox_pair[stamp] = ([name, mtu, device_record, [rto1, rto2]])
            trio[stamp] = (trio_list)
            dumps(f"{name}_pairmode.json", iox_pair)
            # trio[time.time()] = ([Ethernet 1577 Wifi 756 HypoMux 586 0.0008])
            dumps(f"{name}_trio.json", trio)
        if 1 == 1:
            #Change to a json format for each device (Ethernet_Wifi)
            trio_fixed = []
            for line in trio:
                try:
                    j1 = trio.get(line)[3]
                    j2 = trio.get(line)[5]
                except:
                    trio_fixed.append(line)
            if len(trio_fixed) > 1:
                print(f"Trio Config is Messed up {line}")
            for line in trio_fixed:
                del trio[line]
            if len(trio.get(next(iter(trio)))) == 7:
                trio1 = set([values[1] for values in trio.values()])
                trio1_all = [values[1] for values in trio.values()]
                trio2 = set([values[3] for values in trio.values()])
                trio2_all = [values[3] for values in trio.values()]
                trio3 = set([values[5] for values in trio.values()])
                trio3_all = [values[5] for values in trio.values()]
                trio1_dic = {}
                for line in trio1:
                    trio1x = []
                    for line_x in trio:
                        if line == trio.get(line_x)[1]:
                            trio1x.append(trio.get(line_x)[6])
                    trio1_best = (sum(trio1x) / len(trio1x))
                    trio1_dic[line] = trio1_best
                trio1_max = max(list(trio1_dic.values()))
                for line in trio1_dic:
                    if trio1_dic.get(line) == trio1_max:
                        trio1_best = line
                trio2_dic = {}
                for line in trio2:
                    trio2x = []
                    for line_x in trio:
                        if line == trio.get(line_x)[3]:
                            trio2x.append(trio.get(line_x)[6])
                    trio2_best = (sum(trio2x) / len(trio2x))
                    trio2_dic[line] = trio2_best
                trio2_max = max(list(trio2_dic.values()))
                for line in trio2_dic:
                    if trio2_dic.get(line) == trio2_max:
                        trio2_best = line
                trio3_dic = {}
                for line in trio3:
                    trio3x = []
                    for line_x in trio:
                        if line == trio.get(line_x)[5]:
                            trio3x.append(trio.get(line_x)[6])
                    trio3_avg = (sum(trio3x) / len(trio3x))
                    trio3_dic[line] = trio3_avg
                trio3_max = max(list(trio3_dic.values()))
                for line in trio3_dic:
                    if trio3_dic.get(line) == trio3_max:
                        trio3_best = line
                v1 = trio.get(next(iter(trio)))[0]
                v2 = trio.get(next(iter(trio)))[2]
                v3 = trio.get(next(iter(trio)))[4]
                rto_iox = loads(f"{name}_rto.json")
                rto_best = multiple_avg_data(rto_iox, 0, 2, 'max')
                syn_best = multiple_avg_data(rto_iox, 1, 2, 'max')
                rto_b, syn_b = rto_check([rto_best, syn_best])
                #print('Best Setting: ', v1, trio1_best, v2, trio2_best, v3, trio3_best, 'Check {Adapter}_.output.json for Full Info')
                test_even = []
                test_odd = []
                even_odd = 'Null'
                ior = loads(f"{name}_avg.json")
                for line in ior:
                    if int(ior.get(line)[1]) % 2 == 0:
                        test_even.append(ior.get(line)[7])
                    else:
                        test_odd.append(ior.get(line)[7])
                if len(test_odd) > 1 and len(test_even) > 1:
                    test1 = (sum(test_even) / len(test_even))
                    test2 = (sum(test_odd) / len(test_odd))
                    if test1 > test2:
                        even_odd = 'Even'
                    else:
                        even_odd = 'Odd'
                virtual_best = virtual_mtu(name)
                print(f"{len(iox)} Best Setting: {v1} {trio1_best} {v2} {trio2_best} {v3} {trio3_best} RTO {rto_best} SYN {syn_best} ({even_odd}) {v3} Virtual MTU {virtual_best}")
                print("Check {Adapter}_.output.json for Full Info")
                iou = loads(f"{name}_quick.json")
                iou[v1] = (trio1_best)
                iou[v2] = (trio2_best)
                iou[v3] = (trio3_best)
                dumps(f"{name}_quick.json", iou)
                #change_mtu(v1, ipv, trio1_best)
                #change_mtu(v2, ipv, trio2_best)
                #change_mtu(v3, ipv, random.choice([trio3_best, virtual_best]))
                #if trio1_all.count(trio1_best) > 500 and trio2_all.count(trio2_best) > 500 and trio3_all.count(trio3_best) > 500:
                #input('Pairing Is Completed.')
                #return(trio1_best)
    except Exception as e:
        print('Pair Mode Setting Issues:', e, name, mtu, stamp)
        traceback.print_exc()
def virtual_mtu(name, adapter_which=None):
    try:
        ior = {}
        iop = loads(f"{name}_pairmode.json")
        mtu_a = {}
        mtu_b = {}
        ion = {}
        for line in iop:
            try:
                a = iop.get(line)
                #Ethernet[0], Eth_Mtu[1], Wifi[2], Wifi_Mtu[3], HypoMux[4], HypoMux_Mtu[5], Score[6]
                ior[str(time.time())] = ([a[0], a[1], a[2][0][0], a[2][0][1], a[2][1][0], a[2][1][1], a[2][1][2]])
            except:
                pass
        if adapter_which == 'HypoMux-Tun' or adapter_which == None:
            v1_best = multiple_avg_data(ior, 1, 6, 'max') # v1_best is Ethernet
            for line in ior:
                if v1_best == ior.get(line)[1]:
                    mtu_a[str(time.time())] = ([ior.get(line)[4], ior.get(line)[5], ior.get(line)[6]])
            v1_bestx = multiple_avg_data(mtu_a, 1, 2, 'max') # v1_bestx is Ethernet to HypoMux
            v1_bestx_line = []
            for line in mtu_a:
                if v1_bestx == mtu_a.get(line)[1]:
                    v1_bestx_line.append(mtu_a.get(line)[2])
            ion[v1_bestx] = (sum(v1_bestx_line) / len(v1_bestx_line))
            v2_best = multiple_avg_data(ior, 3, 6, 'max') # v2_best is Wifi
            for line in ior:
                if v2_best == ior.get(line)[3]:
                    mtu_b[str(time.time())] = ([ior.get(line)[4], ior.get(line)[5], ior.get(line)[6]])
            v2_bestx = multiple_avg_data(mtu_b, 1, 2, 'max') # v2_bestx is Wifi to HypoMux
            v2_bestx_line = []
            for line in mtu_b:
                if v2_bestx == mtu_b.get(line)[1]:
                    v2_bestx_line.append(mtu_b.get(line)[2])
            ion[v2_bestx] = (sum(v2_bestx_line) / len(v2_bestx_line))
            v3_bestx = multiple_avg_data(ior, 5, 6, 'max')
            v3_bestx_line = []
            for line in ior:
                if v3_bestx == ior.get(line)[5]:
                    v3_bestx_line.append(ior.get(line)[6])
            ion[v3_bestx] = (sum(v3_bestx_line) / len(v3_bestx_line))
            v4_best = max(ion.values())
            for line in ion:
                if v4_best == ion.get(line):
                    v4_best_mtu = line
            return (v4_best_mtu)
        else:
            iot = loads(f"{name}_quick.json")
            adapter_best = iot.get(adapter_which)
            return(adapter_best)
    except Exception as e:
        print('Virtual MTU Issues:', e)
        traceback.print_exc()
def multiple_avg_data(iox, multiple, value_x, type):
    try:
        #iox is a dict, multiple is reoccuring number set() - Location, value_x is a changing score Location
        v1 = set([values[multiple] for values in iox.values()])
        v1_dic = {}
        for line in v1:
            v1_list = []
            for line_x in iox:
                if line == iox.get(line_x)[multiple]:
                    v1_list.append(iox.get(line_x)[value_x])
            v1_dic[line] = (sum(v1_list) / len(v1_list))
        if type == 'min':
            v1_values = min(list(v1_dic.values()))
        elif type == 'max':
            v1_values = max(list(v1_dic.values()))
        for line in v1_dic:
            if v1_values == v1_dic.get(line):
                v1_best = line
        return(v1_best)
    except Exception as e:
        print('Multiple Avg Data Issues:', e)
        return(1500)
# Run intilization Devices + Current Adapter as a list
def get_buffer(name, type):
    try:
        ps = (
            f'Get-NetAdapterAdvancedProperty -Name "{name}" '
            f'| Where-Object {{ $_.DisplayName -match "Buffer" }} '
            f'| ForEach-Object {{ "$($_.DisplayName)=$($_.DisplayValue)" }}'
        )
        result = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
        buffers = {}
        for line in result.stdout.strip().splitlines():
            if "=" in line:
                key, val = line.split("=", 1)
                buffers[key.strip()] = int(val.strip())
        r_x = buffers.get("Receive Buffers", 0)
        t_x = buffers.get("Transmit Buffers", 0)
        if type == 'r':
            return(r_x)
        elif type == 't':
            return(t_x)
    except Exception as e:
        print('Get Buffer Issues:', e)
def update_buffer(name, type, value_x):
    try:
        rx_cmd = (
            f'Set-NetAdapterAdvancedProperty -Name "{name}" '
            f'-DisplayName "Receive Buffers" -DisplayValue {value_x}'
        )
        tx_cmd = (
            f'Set-NetAdapterAdvancedProperty -Name "{name}" '
            f'-DisplayName "Transmit Buffers" -DisplayValue {value_x}'
        )
        if type == 'r':
            result_type = 'Recieve'
            old_buffer = get_buffer(name, 'r')
            result = subprocess.run(["powershell", "-NoProfile", "-Command", rx_cmd], capture_output=True, text=True)
        elif type == 't':
            result_type = 'Transmit'
            old_buffer = get_buffer(name, 't')
            result = subprocess.run(["powershell", "-NoProfile", "-Command", tx_cmd], capture_output=True, text=True)
        print(f'{name} Swapped {result_type} Buffer {old_buffer} : {value_x} => {result}')
    except Exception as e:
        print('Update Buffer Issues:', e)
def buffers(name, stamp, n_score):
    try:
        iox = loads(f"{name}_buffers.json")
        iox[stamp] = ([get_buffer(name, 'r'), get_buffer(name, 't'), n_score])
        dumps(f"{name}_buffers.json", iox)
        receive_buffer_best = multiple_avg_data(iox, 0, 2, 'max')
        transmit_buffer_best = multiple_avg_data(iox, 1, 2, 'max')
        return(receive_buffer_best, transmit_buffer_best)
    except Exception as e:
        print('Buffer Issues: ', e)
def rto_check(rto_i=None):
    try:
        if rto_i != None:
            rto_time = rto_i[0]
            rto_syn = rto_i[1]
            command = f"netsh interface tcp set global initialRto={rto_time} maxsynretransmissions={rto_syn}"
            result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True)
            #result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        result1 = subprocess.run(["netsh", "interface", "tcp", "show", "global"],capture_output=True, text=True, check=True)
        output = result1.stdout
        rto_match = re.search(r"Initial RTO\s*:\s*(\d+)", output)
        rto = int(rto_match.group(1)) if rto_match else None
        syn_match = re.search(r"Max SYN Retransmissions\s*:\s*(\d+)", output)
        max_syn = int(syn_match.group(1)) if syn_match else None
        return(rto, max_syn)
    except Exception as e:
        print('RTO Check Issues:', e)
def measure(ip):
    host = pingx(ip, count=3, interval=1, timeout=2)
    received = host.packets_received
    ratio = (host.avg_rtt / host.max_rtt) if host.max_rtt > 0 else 0
    alive = host.is_alive
    return(ip, ratio, alive, received)
def lan_scan():
    try:
        ip_index = list(range(0, 16))
        devices = []
        total = 384
        total_r = 0
        ioz = loads('Simple Terra Exchange.json')
        ioz_list = list(ioz.values())
        ioz_min = min(ioz_list)
        ioz_max = max(ioz_list)
        for line in ioz:
            if ioz_min == ioz.get(line):
                net_min = line
            elif ioz_max == ioz.get(line):
                net_max = line
        #AUD : .au
        #CAD : .ca
        #CHF : .ch
        #CNY : .cn
        #DKK : .dk
        #EUR : .eu
        #GBP : .uk
        #HKD : .hk
        #IDR : .id
        #INR : .in
        #JPY :
        #KRW
        #MYR
        #NOK
        #PHP
        #SDR
        #SEK
        #THB
        #USD
        net_dic = {'uaud': ['170.64.147.31', '172.193.67.34', '13.239.88.95', '54.252.183.5', '54.252.183.4', '118.127.62.178', '45.248.78.99', '103.12.189.171'],
                   'ucad': ['96.45.46.46', '99.240.73.140', '69.70.21.150', '132.145.108.223', '91.194.11.222', '38.110.76.234', '172.94.127.12', '69.79.228.166'],
                   'uchf': ['192.0.66.156', '217.26.52.52', '170.17.153.89', '80.219.100.93', '81.63.150.156', '46.14.186.141', '62.2.151.66', '46.14.199.129'],
                   'ucny': ['8.218.126.38', '103.144.53.186', '223.5.5.252', '120.53.53.198', '114.114.115.115', '103.144.52.214', '173.82.141.168', '120.53.53.54'],
                   'udkk': ['88.221.162.33', '46.166.189.67', '80.113.19.90', '213.125.136.58', '51.158.152.202', '89.146.35.15', '145.131.193.46', '84.31.128.12'],
                   'ueur': ['89.96.201.83', '195.250.235.162', '82.97.230.90', '119.12.45.8', '195.101.69.86', '212.234.30.110', '86.218.132.205', '80.124.101.202'],
                   'ugbp': ['81.138.71.238', '143.110.169.182', '192.221.154.0', '80.235.229.76', '81.150.170.21', '62.31.244.147', '82.71.43.40', '77.98.166.200'],
                   'uhkd': ['209.146.104.69', '223.255.177.202', '119.9.73.44', '42.3.117.64', '221.126.236.36', '113.255.5.34', '219.78.193.143', '72.255.228.180'],
                   'uidr': ['103.159.195.156', '124.40.249.202', '103.189.197.81', '202.43.162.37', '103.147.76.65', '103.3.213.17', '103.111.29.102', '202.55.161.17'],
                   'uinr': ['136.232.85.66', '115.98.145.166', '120.59.16.25', '182.18.187.27', '182.156.154.150', '36.50.50.50', '175.101.8.251', '115.97.193.195'],
                   'ujpy': ['203.141.131.66', '116.80.58.204', '125.206.12.134', '118.3.227.163', '121.119.170.152', '116.91.115.190', '217.178.113.53', '121.107.13.224'],
                   'ukrw': ['210.118.170.15', '121.166.66.139', '222.97.189.7', '27.126.19.30', '119.56.228.48', '59.29.114.72', '210.106.213.69', '112.185.179.12'],
                   'umyr': ['103.173.114.104', '49.236.193.35', '123.253.33.86', '103.169.90.58', '211.25.202.171', '183.171.9.237', '58.71.196.96', '203.176.144.12'],
                   'unok': ['217.168.95.249', '88.88.141.239', '81.175.38.1', '85.200.247.5', '79.161.86.212', '89.162.60.40', '178.23.102.48', '85.89.0.89'],
                   'uphp': ['27.110.152.250', '210.5.72.2', '112.198.179.23', '155.137.127.22', '115.146.170.75', '58.69.197.2', '124.6.167.108', '206.62.42.19'],
                   'usdr': ['46.59.22.19', '83.253.190.231', '77.53.225.88', '130.244.126.100', '91.190.142.200', '85.11.24.148', '81.170.202.134', '188.149.226.3'],
                   'usek': ['213.165.181.14', '84.255.35.91', '84.255.41.14', '195.158.87.192', '194.105.32.2', '195.158.94.17', '84.255.32.87', '213.165.169.162'],
                   'uthb': ['61.7.231.22', '110.49.24.138', '110.49.26.197', '61.19.146.204', '118.174.65.213', '61.7.143.128', '202.28.35.169', '110.78.165.53'],
                   'uusd': ['204.106.240.53', '108.179.34.214', '162.243.184.122', '72.14.119.153', '50.223.52.23', '65.144.94.241', '137.184.80.190', '74.112.213.130']}
        for line in ip_index:
            devices.append(f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}")
            devices.append(f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}")
            devices.append(f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}")
            devices.append(f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}")
            devices.append(f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}")
            devices.append(f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}")
            devices.append(f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}")
            devices.append(f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}")
        devices.remove(devices[0])
        devices.remove(devices[5])
        devices.remove(devices[10])
        devices.remove(devices[25])
        # These are two devices on my own network that I use to verify it's a real device, it's IPv4 yes.
        # Because your network can be re routed multiple times to different servers it can affect testing.
        devices.append('192.168.1.190')
        devices.append('192.168.1.1')
        devices.append('192.168.1.164')
        devices.append('192.168.1.157')
        net_min_list = net_dic.get(net_min)
        net_max_list = net_dic.get(net_max)
        try:
            for line in net_min_list:
                devices.append(line)
        except:
            print(f"Need to add {net_min} to Lan Scan")
        try:
            for line in net_max_list:
                devices.append(line)
        except:
            print(f"Need to add {net_max} to Lan Scan")
        lan_list = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(measure, ip): ip for ip in devices}
            for future in as_completed(futures):
                ip, ratio, alive, received = future.result()
                if alive == True:
                    lan_list.append(ratio)
                    total_r = (total_r + received)
                else:
                    total = (total - 3)
        lan_score = (1 / ((((sum(lan_list) / len(lan_list)) / max(lan_list)) + (total / total_r)) / 2))
        return(lan_score)
    except Exception as e:
        print('Lan Score Issues:', e)
def rto_engine(max_recheck, name, rto_work, syn_work):
    try:
        if max_recheck == 0:
            rto_dic = loads(f"{name}_rto.json")
            rto_have = list(set([values[0] for values in rto_dic.values()]))
            syn_have = list(set([values[1] for values in rto_dic.values()]))
            rto_work1 = []
            syn_work1 = []
            for line in rto_work:
                if line not in rto_have:
                    rto_work1.append(line)
            for line in syn_work:
                if line not in syn_work:
                    syn_work1.append(line)
            if len(rto_work1) > 0:
                print(f"RTO: {len(rto_work1)}")
                rto_best = random.choice(rto_work1)
            else:
                rto_best = multiple_avg_data(rto_dic, 0, 2, 'max')
            if len(syn_work1) > 0:
                syn_best = random.choice(syn_work1)
            else:
                syn_best = multiple_avg_data(rto_dic, 1, 2, 'max')
            rto_a, syn_a = rto_check([rto_best, syn_best])
        elif max_recheck == 2:
            rto_a, syn_a = rto_check([random.choice(rto_work), random.choice(syn_work)])
        else:
            iox = loads(f"{name}.json")
            iop = loads(f"{name}_pairmode.json")
            rto_dic = {}
            rto_list = list(iox.keys() & iop.keys())
            for line in rto_list:
                try:
                    rto_listx = [iop.get(line)[3][0], iop.get(line)[3][1]]
                    rto_listx.append(iox.get(line)[7])
                    rto_dic[line] = (rto_listx)
                except:
                    pass
            dumps(f"{name}_rto.json", rto_dic)
            rto_best = multiple_avg_data(rto_dic, 0, 2, 'max')
            syn_best = multiple_avg_data(rto_dic, 1, 2, 'max')
            rto_b, syn_b = rto_check([rto_best, syn_best])
    except Exception as e:
        print('RTO Engine Issues:', e)
def pair_mode_engine(max_recheck, name, ipv, device_list_work):
    try:
        if max_recheck == 0:
            xi1 = list(device_list_work.keys())
            for line in xi1:
                xi = change_mtu(line, ipv, random.choice(device_list_work.get(line)))
        else:
            xi1 = list(device_list_work.keys())
            for line in xi1:
                xi2 = virtual_mtu(name, line)
                xi = change_mtu(line, ipv, xi2)
    except Exception as e:
        print('Pair Mode Engine Issues:', e)
def pair_mode_engine2(max_recheck, name, b, ipv, n, interface_list):
    try:
        #if max_recheck == 0:
        pair_mode_settings(name, b, ipv, n, interface_list)
        #pair_mode_settings(name, b, ipv, n, interface_list, 1)
    except Exception as e:
        print('Pair Mode Engine 2 Issues:', e)
def main_adapter_engine(max_recheck, work, name, ipv, pair_mode):
    try:
        v1 = work
        if pair_mode == 1:
            iop = loads(f"{name}_pairmode.json")
            v2 = []
            #v2 = list(set([values[1] for values in iop.values()]))
            for line in iop:
                try:
                    v2.append(int(iop.get(line)[1]))
                except:
                    pass
            v2 = list(set(v2))
            try:
                for line in v2:
                    if line in work:
                        v1.remove(line)
            except Exception as e:
                pass
            ioz = loads(f"{name}_quick.json")
            main_best = ioz.get(next(iter(ioz)))
            if max_recheck == 0:
                if len(v1) > 1:
                    print(f"{name} MTU To Process", len(v1))
                    main_best = random.choice(v1)
                    b = change_mtu(name, ipv, main_best)
                else:
                    b = change_mtu(name, ipv, main_best)
            else:
                b = change_mtu(name, ipv, main_best)
        else:
            iox = loads(f"{name}.json")
            v2 = []
            #main_best = ioz.get(next(iter(ioz)))
            for line in iox:
                try:
                    v2.append(int(iox.get(line)[1]))
                except:
                    pass
            v2 = list(set(v2))
            try:
                for line in v2:
                    if line in work:
                        v1.remove(line)
            except Exception as e:
                pass
            main_best = multiple_avg_data(iox, 0, 7, 'max')
            if max_recheck == 0:
                if len(v1) > 1:
                    print(f"{name} MTU To Process", len(v1))
                    main_best = random.choice(v1)
                    b = change_mtu(name, ipv, main_best)
                else:
                    b = change_mtu(name, ipv, main_best)
            else:
                b = change_mtu(name, ipv, main_best)
        print(f"{name} Trying: {main_best}")
    except Exception as e:
        print('Main Adapter Engine Issues:', e)
        traceback.print_exc()
def cmd_mtu():
    try:
        result = subprocess.run(["powershell", "-Command", "Get-NetIPInterface | Format-Table InterfaceAlias,AddressFamily,NlMtu,ConnectionState"], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except Exception as e:
        print('CMD MTU Issues:', e)
def display_error():
    try:
        print('So the connection dropped, rubbish.')
        time.sleep(3)
        print('You know you can really mess up stuff playing around with registry.')
        time.sleep(10)
        print('Computer\\HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters')
        print('Running CMD in admin using Powershell you can run >>> Get-NetAdapter | Select-Object Name, InterfaceGuid, InterfaceDescription')
        print('Also can run >>> Get-NetIPInterface | Format-Table InterfaceAlias,AddressFamily,NlMtu,ConnectionState')
        print('Buffer Issues >>> Get-NetAdapterAdvancedProperty -Name "Ethernet" | Where-Object { $_.DisplayName -match "Buffer" }')
        print('Sometimes Wifi has 0 buffers meaning no limitation')
        print('Device Manager => Network Adapters')
        print('>>> Get-Counter -ListSet * | Where-Object CounterSetName -match "Network" | Select-Object CounterSetName')
        print('>>> https://mags.acm.org/communications/201203/?pg=48#pg48')
        print('>>> https://www.youtube.com/watch?v=iSHFa4EXyjQ')
        print('>>> netsh interface tcp set global initialRto=450 maxsynretransmissions=2')
        print('>>> netsh int tcp set global pacingprofile=always')
        print('>>> netsh int tcp show global')
        print('>>> netsh int tcp set global ecncapability=enabled')
        print('TcpAckFrequency 1 TcpDelAckTicks 0 TcpNoDelay 1 TcpTimedWaitDelay 30 FastSendDatagramThreshold 9000 (IP MTU L3)')
        print('Sack0pts 1, Tcp1323Opts 2, EnablePMTUBHDetect 1')
        print('>>> Get-NetAdapterRss | Format-Table Name, Enabled, NumberOfReceiveQueues, Profile -AutoSize')
        print('>>> Get-NetAdapterRss -Name "Ethernet" | Format-List *')
        print('https://github.com/vadyaravadim/msi-mode-utility')
        print('>>> Set-NetAdapterRss -Name "Ethernet" -BaseProcessorNumber 0 -MaxProcessorNumber 15 -MaxProcessors 16')
        print('>>> ping -n 8 -l 65500 192.168.1.1')
        print('>>> netsh int tcp show supplemental')
        print('>>> netsh int tcp set supplemental help')
        print('>>> Get-NetTCPSetting | Format-Table SettingName, CongestionProvider -AutoSize')
        print('>>> netsh int tcp set supplemental template=internetcustom congestionprovider=cubic')
        # Enable Lower delayedackfrequency=1 & MSS
        print('>>> Get-NetTCPSetting | Format-List SettingName,*')
        print('>>> netsh int tcp set supplemental template=internet enablecwndrestart=enabled')
        print('Computer\\HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Services\\Ndu (Start = 4)')
        print('netsh int ipv4 show dynamicport udp')
        print('Get-NetTCPSetting | Format-Table SettingName,AutoTuningLevelLocal,AutoTuningLevelGroupPolicy,ScalingHeuristics,InitialRtoMs -AutoSize')
        print('netsh int tcp set global autotuninglevel=experimental')
        print('netsh int tcp set heuristics enabled')
        print('HKLM\\System\\CCS\\Control\\SessionManager\\Kernel\\ThreadDpcEnable  (Set to 1)')
        print('https://xiking.win/2020/05/15/1-linux-network-multiqueue/')
    except Exception as e:
        print('Display Error Issues:', e)
def wait_engine(name, ipv):
    try:
        iox = loads(f"{name}.json")
        iox_len = len(iox)
        print('')
        print(f"Verify you ran CMD in Admin. Data Set: {iox_len}")
        print('')
        if iox_len > 5500:
            ioz = loads(f"{name}_quick.json")
            for line in ioz:
                print(line, ioz.get(line))
                ba = change_mtu(line, ipv, ioz.get(line))
            gc.collect()
        if iox_len > 50:
            iox_wait = (iox_len // 2)
            time.sleep(iox_wait)
        cmd_mtu()
    except Exception as e:
        print('Wait Engine Issues:', e)
def main():
    try:
        print('##### Anthonys MTU Adjuster #####')
        print('')
        print('Run As Admin To Change MTU')
        print('cd into folder')
        print('python "2026 - Mtu(press tab)"')
        print('Jumbo Ethernet Frames & Hyper-V 65536')
        print('10 Gigabit Server Adapters: Transmit Buffers 16384')
        print('Standard Computers use Even Stepping')
        print('Quantum Computers use Odd unless its built with tri chips')
        print('On Desktop Computers the fans need to be monitored by speed, 5watt fan vs 500w system Fan may be increasing in speed')
        print('')
        interfaces = list(psutil.net_if_addrs().keys())
        print(interfaces)
        pair_mode = 0
        max_buffer_dic = {}
        device_list_work = {}
        rto_min = int(input('Min RTO: '))
        rto_max = int(input('Max RTO: '))
        syn_max = int(input('Max SYN: '))
        rto_work = list(range(rto_min, (rto_max + 10), 10))
        syn_work = list(range(1, (syn_max + 1), 1))
        for name in interfaces:
            print('')
            confirm = input(f"Benchmark {name} Y/N: ")
            if confirm.lower() == 'y':
                all_interfaces = [name]
                print('')
                print('')
                print('########################################')
                print(f">>>>> {name} <<<<<")
                print('')
                print('***** Testing Range *****')
                print('z: Skip Testing And Set MTU')
                print('y: MTU Pair Mode')
                print('x: Change Adapters Buffer')
                print('0: Custom Value')
                print('1: IPV4 576 => 9014 (Jumbo Frame) Steps of 64')
                print('2: IPV4 576 => 9014 (Jumbo Frame) Steps of 32')
                print('3: IPV4 576 => 9014 (Jumbo Frame) Steps of 8')
                print('4: IPV4 576 => 9014 (Jumbo Frame) Steps of 1')
                print('5: IPV4 576 => 1500 (Standard Frame) Steps of 64')
                print('6: IPV4 576 => 1500 (Standard Frame) Steps of 32')
                print('7: IPV4 576 => 1500 (Standard Frame) Steps of 8')
                print('8: IPV4 576 => 1500 (Standard Frame) Steps of 2')
                print('9: IPV4 576 => 1500 (Standard Frame) Steps of 1')
                print('########################################')
                print('')
                a = str(input('Choice: '))
                print('')
                if a == '0':
                    ipv = str(input('IPV4 or IPV6 Type either 4/6: '))
                    if ipv == '4':
                        ipv = 'IPV4'
                    elif ipv == '6':
                        ipv = 'IPV6'
                    start_range = int(input('Start Range: '))
                    end_range = int(input('End Range: '))
                    step_range = int(input('In Steps 1,2,3,8,16,32: '))
                elif a == 'z':
                    ipv = str(input('IPV4 or IPV6 Type either 4/6: '))
                    if ipv == '4':
                        ipv = 'IPV4'
                    elif ipv == '6':
                        ipv = 'IPV6'
                    z1 = int(input('MTU Set: '))
                    k = change_mtu(name, ipv, z1)
                    print(f"{name} Set MTU: {k}")
                elif a == 'x':
                    type = input('R/T: ').lower()
                    value_x = int(input('Value: '))
                    update_buffer(name, type, value_x)
                    continue
                elif a == '3':
                    ipv = 'IPV4'
                    step_range = 1
                    end_range = 9014
                    start_range = 576
                elif a == '8':
                    ipv = 'IPV4'
                    step_range = 2
                    end_range = 1500
                    start_range = 576
                elif a == '9':
                    ipv = 'IPV4'
                    step_range = 1
                    end_range = 1500
                    start_range = 576
                elif a == '5':
                    ipv = 'IPV4'
                    step_range = 64
                    end_range = 1500
                    start_range = 576
                elif a == '6':
                    ipv = 'IPV4'
                    step_range = 32
                    end_range = 1500
                    start_range = 576
                elif a == '4':
                    ipv = 'IPV4'
                    step_range = 8
                    end_range = 9014
                    start_range = 576
                elif a == '7':
                    ipv = 'IPV4'
                    step_range = 8
                    end_range = 1500
                    start_range = 576
                    source_ip = '192.168.1.170'
                elif a == '1':
                    ipv = 'IPV4'
                    step_range = 64
                    end_range = 9014
                    start_range = 576
                elif a == '2':
                    ipv = 'IPV4'
                    step_range = 32
                    end_range = 9014
                    start_range = 576
                elif a == 'y':
                    pair_mode = 1
                    interface_list = []
                    ipv = 'IPV4'
                    start_range = 576
                    end_range = int(input('End Range: '))
                    step_range = int(input('In Steps 1,2,3,8,16,32: '))
                    interface_x = list(psutil.net_if_addrs().keys())
                    device_list_work = {}
                    min_buffer_size = 32
                    max_buffer_dic = {}
                    for line in interface_x:
                        confirm = input(f"Pair Interface {line} Y/N: ")
                        if confirm.lower() == 'y':
                            interface_list.append(line)
                            end_range1 = int(input('Max MTU Size: '))
                            work1 = list(range(start_range, (end_range1 + step_range), step_range))
                            device_list_work[line] = (work1)
                            all_interfaces.append(line)
                    for line in all_interfaces:
                        confirm = input(f"Change Buffer Sizes on {line} Y/N: ")
                        if confirm.lower() == 'y':
                            max_buffer = int(input(f'{line} Max Buffer Size:'))
                            work2 = list(range(min_buffer_size, (max_buffer + step_range), step_range))
                            max_buffer_dic[line] = (work2)
                ip_source = next((a.address for a in psutil.net_if_addrs().get(name, []) if a.family == 2), None)
                iu = get_mtu(name, ipv)
                change_mtu(name, ipv, start_range)
                work = list(range(start_range, (end_range + step_range), step_range))
                buff_change = 0
                admin_error = 1
                error1 = 0
                max_recheck = 0
                old_mtu = iu
                do_once = 0
                try:
                    while True:
                        # RTO & SYN
                        #print('Start')
                        rto_engine(max_recheck, name, rto_work, syn_work)
                        #print('Completed: RTO')
                        if pair_mode == 1:
                            #MTU Extra Devices
                            pair_mode_engine(max_recheck, name, ipv, device_list_work)
                            #print("Completed: Pair Mode Engine")
                        # Main Adapter has Pair Mode Settings
                        main_adapter_engine(max_recheck, work, name, ipv, pair_mode)
                        #print('Completed: Main Adapter Engine')
                        #print()
                        #if max_recheck > 3:
                        #max_recheck = 0
                        #if pair_mode == 1:
                        #number = pair_mode_settings(name, b, ipv, n, interface_list, 1)
                        #if int(b) == int(number):
                        b = get_mtu(name, ipv)
                        if 1 == 1:
                            print(f"{name} {iu} Old: {old_mtu} => New: {b}")
                            checker, n, g2_score = speed_tester(name, b)
                            #print('Completed: Speed Tester')
                            if checker == 0:
                                print(f"Speed Tester issues running {name}")
                                if error1 == 0:
                                    display_error()
                                    qrcode = segno.make_qr('https://mags.acm.org/communications/201203/?pg=48#pg48')
                                    qrcode.save('Mags.png', scale=10, )
                                    time.sleep(10)
                                    no_internet_boot()
                                    error1 == 1
                                continue
                            if checker == 0:
                                input(f"Make Sure these arent 0 {n} {g2_score}")
                            #= scoring(name, b, download, upload, ping)
                            # Ignoring Buffers Because I don't have it working on my system yet
                            # But the code logic is implemented, probably has issues.
                            best_buffers = []
                            if len(max_buffer_dic) > 1:
                                for line in all_interfaces:
                                    r, t = buffers(line, n, g2_score)
                                    best_buffers.append([line, r, t])
                                    if buff_change < 24:
                                        update_buffer(name, 'r', random.choice(max_buffer_dic.get(line)))
                                        update_buffer(name, 't', random.choice(max_buffer_dic.get(line)))
                                print('Adapter, Recieve, Transmit:', best_buffers)
                            if buff_change < 24:
                                buff_change = (buff_change + 1)
                            else:
                                buff_change = 0
                            if pair_mode == 1:
                                #pair_mode_settings(name, b, ipv, n, interface_list)
                                pair_mode_engine2(max_recheck, name, b, ipv, n, interface_list)
                                #print('Completed: Pair Mode Engine 2')
                                #print('Completed: Pair Mode Engine2')
                            #num_max = scoring_output(name, ipv)
                            scoring_output(name, ipv)
                            #print('Completed: Scoring Output')
                            #a = b
                            old_mtu = get_mtu(name, ipv)
                        else:
                            print('Issues')
                            if admin_error == 1:
                                print('Run As Admin')
                                admin_error = 0
                        max_recheck = (max_recheck + 1)
                        if max_recheck > 4:
                            max_recheck = 0
                        do_once = 1
                        wait_engine(name, ipv)
                except KeyboardInterrupt:
                    print('Exited Loop')
                iu_x = change_mtu(name, ipv, iu)
        print('')
        input('Exit Program')
    except Exception as e:
        print('Main Issues:', e)
        traceback.print_exc()
while True:
    main()

#############################################################################################################
#Depreciated Functions
def python_ping(name, mtu, source_ip):
    try:
        iox = loads(f"{name}_router.json")
        interval = 0.01
        timeout = 0.5
        h = ping("192.168.1.1", count=250, interval=interval, timeout=timeout, source=source_ip, privileged=False)
        #stats = [interval, timeout, h.packets_sent, h.packets_received, h.packet_loss, h.min_rtt, h.avg_rtt, h.max_rtt, h.jitter]
        #print(stats)
        iox[time.time()] = ([mtu, interval, timeout, h.avg_rtt])
        #all_mtu_total = [values[0] for values in iox.values()]
        all_mtu = set([values[0] for values in iox.values()])
        dumps(f"{name}_router.json", iox)
        iox_t = {}
        for line in all_mtu:
            o = []
            for line_x in iox:
                if line == iox.get(line_x)[0]:
                    o.append(iox.get(line_x)[3])
            o_avg = (sum(o) / len(o))
            iox_t[time.time()] = ([name, source_ip, line, o_avg])
        iox = iox_t
        min_avg = min(set([values[3] for values in iox.values()]))
        if 0 == int(min_avg):
            print('Ping 0 Issues...Superquick')
        else:
            for line in iox:
                if min_avg == iox.get(line)[3]:
                    print('Lowest Router Ping: ', iox.get(line))
        dumps(f"{name}_router_avg.json", iox)
    except Exception as e:
        print('Python Ping Issues: ', e)