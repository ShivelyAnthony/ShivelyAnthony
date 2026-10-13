# MTU Adjuster Anthony R Shively (Mercer Ohio 1997)
# If this software is used in Machine Learning, mention source of where it was found.

#Get-NetIPInterface | Format-Table InterfaceAlias,AddressFamily,NlMtu,ConnectionState
#Set-NetIPInterface -InterfaceAlias "Wi-Fi" -AddressFamily IPv4 -NlMtuBytes 800
import subprocess
import random
import json
import os
import time
import psutil
import speedtest
import socket
import re
import traceback
from icmplib import ping
from PyLibreHardwareMonitor import Computer
#from rich.progress import track
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
def get_temps():
    try:
        temps = []
        load = []
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
        print('MTU Max Download: ', download_index[0], download_index[1], download_index[2], download_index[3], download_index[4], download_index[5], int(download_index[6]), download_index[7], all_mtus.count(download_index[1]))
        print('MTU Max Upload: ', upload_index[0], upload_index[1], upload_index[2], upload_index[3], upload_index[4], upload_index[5], int(upload_index[6]), upload_index[7], all_mtus.count(upload_index[1]))
        print('MTU Lowest Ping: ', ping_index[0], ping_index[1], ping_index[2], ping_index[3], ping_index[4], ping_index[5], int(ping_index[6]), ping_index[7], all_mtus.count(ping_index[1]))
        print('Max MTU Score: ', score_index[0], score_index[1], score_index[2], score_index[3], score_index[4], score_index[5], int(score_index[6]), score_index[7], all_mtus.count(score_index[1]))
        print('Min Load Temp:', load_temp_index[0], load_temp_index[1], load_temp_index[2], load_temp_index[3], load_temp_index[4], load_temp_index[5], int(load_temp_index[6]), load_temp_index[7], all_mtus.count(load_temp_index[1]))
        print('Max Load Temp Score:', load_temp_score_index[0], load_temp_score_index[1], load_temp_score_index[2], load_temp_score_index[3], load_temp_score_index[4], load_temp_score_index[5], int(load_temp_score_index[6]), load_temp_score_index[7], all_mtus.count(load_temp_index[1]))
        ran_pick = [ping_index[1], score_index[1], upload_index[1], download_index[1], load_temp_index[1], load_temp_score_index[1]]
        if all_mtus.count(load_temp_score_index[1]) > 50:
            iop = change_mtu(name, ipv, load_temp_score_index[1])
            input('Program Finished: ', name, load_temp_score_index[1])
        quick_pick = random.choice(ran_pick)
        return(quick_pick)
    except Exception as e:
        print('Scoring Output Issues: ', e)
        traceback.print_exc()
def scoring(name, mtu, download, upload, ping):
    iox = loads(f"{name}.json")
    score = (((download * .5) + (upload * .5)) / (ping))
    tn = str(time.time())
    g1, g2 = get_temps()
    g2_score = (score / g2)
    iox[tn] = ([name, mtu, download, upload, ping, score, g2, g2_score])
    dumps(f"{name}.json", iox)
    return(tn, g2_score)
def speed_tester():
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
        return(download, upload, ping, 1)
    except Exception as e:
        return(0, 0, 0, 0)
        #print('Speed Tester Issues:', e)
def get_mtu(name, ipv):
    try:
        command = (f'Get-NetIPInterface -InterfaceAlias "{name}" ' f'-AddressFamily {ipv} | ' 'Select-Object -ExpandProperty NlMtu')
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
        command = (f'Set-NetIPInterface -InterfaceAlias "{name}" ' f'-AddressFamily {ipv} -NlMtuBytes {mtu}')
        #command = ["powershell.exe", "-NoProfile", "-Command", f'Set-NetIPInterface -InterfaceAlias "{name}" ' f'-AddressFamily {ipv} -NlMtuBytes {mtu}']
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, text=True)
        #print(result)
        b = get_mtu(name, ipv)
        time.sleep(2)
        return(b)
    except Exception as e:
        print('Changing MTU Issues:', e)
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
        if u == None:
            trio_list = [name, mtu]
            #Record MTU Devices
            device_record = []
            for line_a in devices:
                device_mtu = get_mtu(line_a, ipv)
                device_record.append([line_a, device_mtu, iox.get(stamp)[7]])
                trio_list.append(line_a)
                trio_list.append(device_mtu)
            trio_list.append(iox.get(stamp)[7])
            iox_pair[stamp] = ([name, mtu, device_record])
            trio[stamp] = (trio_list)
            dumps(f"{name}_pairmode.json", iox_pair)
            # trio[time.time()] = ([Ethernet 1577 Wifi 756 HypoMux 586 0.0008])
            dumps(f"{name}_trio.json", trio)
        else:
            #Change to a json format for each device (Ethernet_Wifi)
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
                print('Best Setting: ', v1, trio1_best, v2, trio2_best, v3, trio3_best)
                change_mtu(v1, ipv, trio1_best)
                change_mtu(v2, ipv, trio2_best)
                change_mtu(v3, ipv, trio3_best)
                if trio1_all.count(trio1_best) > 500 and trio2_all.count(trio2_best) > 500 and trio3_all.count(trio3_best) > 500:
                    input('Pairing Is Completed.')
            return(trio1_best)
    except Exception as e:
        print('Pair Mode Setting Issues:', e, name, mtu, stamp)
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
def main():
    try:
        print('##### Anthonys MTU Adjuster #####')
        print('')
        print('Run As Admin To Change MTU')
        print('cd into folder')
        print('python "2026 - Mtu(press tab)"')
        print('Jumbo Ethernet Frames & Hyper-V 65536')
        print('10 Gigabit Server Adapters: Transmit Buffers 16384')
        print('')
        interfaces = list(psutil.net_if_addrs().keys())
        print(interfaces)
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
                print('8: IPV4 576 => 1500 (Standard Frame) Steps of 1')
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
                a = iu
                zen = 0
                try:
                    while True:
                        if max_recheck > 3:
                            max_recheck = 0
                            #number = num_max
                            if pair_mode == 1:
                                number = pair_mode_settings(name, b, ipv, n, interface_list, 1)
                                zen = 1
                        elif max_recheck == 3:
                            if pair_mode == 1:
                                v1 = work
                                iop = loads(f"{name}_pairmode.json")
                                v2 = set([values[1] for values in iop.values()])
                                try:
                                    for line in v2:
                                        if line in work:
                                            v1.remove(line)
                                except Exception as e:
                                    pass
                                if len(v1) > 1:
                                    number = random.choice(v1)
                                else:
                                    number = num_max
                        else:
                            number = random.choice(work)
                        print(f"{name} Trying: {number}")
                        if zen == 0:
                            b = change_mtu(name, ipv, number)
                            if pair_mode == 1:
                                #ki_list = list(range(0, len(device_list_work)))
                                #ki = random.choice(ki_list)
                                #ki_key = device_list_work.keys()
                                ki = random.choice(list(device_list_work.keys()))
                                xi = change_mtu(ki, ipv, random.choice(device_list_work.get(ki)))
                        else:
                            b = number
                            zen = 0
                        if int(b) == int(number):
                            print(f"{name} {iu} Old: {a} => New: {b}")
                            python_ping(name, b, ip_source)
                            download, upload, ping, checker = speed_tester()
                            if checker == 0:
                                print(f"Speed Tester issues running {name}")
                                if error1 == 0:
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
                                    time.sleep(10)
                                    no_internet_boot()
                                    error1 == 1
                                continue
                            n, g2_score = scoring(name, b, download, upload, ping)
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
                                pair_mode_settings(name, b, ipv, n, interface_list)
                            num_max = scoring_output(name, ipv)
                            a = b
                        else:
                            if admin_error == 1:
                                print('Run As Admin')
                                admin_error = 0
                        max_recheck = (max_recheck + 1)
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
