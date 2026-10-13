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
        quick_index = {ping_index[1] : ping_index[0],
                       score_index[1] : score_index[0],
                       upload_index[1] : upload_index[0],
                       download_index[1] : download_index[0],
                       load_temp_index[1] : load_temp_index[0],
                       load_temp_score_index[1] : load_temp_score_index[0]}
        if all_mtus.count(load_temp_score_index[1]) > 50:
            iop = change_mtu(name, ipv, load_temp_score_index[1])
            input('Program Finished: ', name, load_temp_score_index[1])
        quick_pick = random.choice(ran_pick)
        return(quick_pick, quick_index.get(quick_pick))
    except Exception as e:
        print('Scoring Output Issues: ', e)
        traceback.print_exc()
def scoring(name, mtu, download, upload, ping):
    iox = loads(f"{name}.json")
    score = (((download * .5) + (upload * .5)) / (ping))
    tn = time.time()
    g1, g2 = get_temps()
    g2_score = (score / g2)
    iox[tn] = ([name, mtu, download, upload, ping, score, g2, g2_score])
    dumps(f"{name}.json", iox)
    return(tn)
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
        iox_pair = loads(f"{name}_pairmode.json")
        if u == None:
            #Record MTU Devices
            device_record = []
            for line_a in devices:
                device_mtu = get_mtu(line_a, ipv)
                device_record.append([line_a, device_mtu])
            iox_pair[stamp] = ([name, mtu, device_record])
            dumps(f"{name}_pairmode.json", iox_pair)
        else:
            if u in iox_pair:
                device_record_read = iox_pair.get(u)[2]
                for line_b in device_record_read:
                    change_mtu(line_b[0], ipv, line_b[1])
                print('Best Setting: ', name, mtu, device_record_read)
    except Exception as e:
        print('Pair Mode Setting Issues:', e)
def main():
    try:
        print('##### Anthonys MTU Adjuster #####')
        print('')
        print('Run As Admin To Change MTU')
        print('cd into folder')
        print('python "2026 - Mtu(press tab)"')
        print('')
        interfaces = list(psutil.net_if_addrs().keys())
        print(interfaces)
        for name in interfaces:
            print('')
            confirm = input(f"Benchmark {name} Y/N: ")
            if confirm.lower() == 'y':
                print('')
                print('')
                print('########################################')
                print(f">>>>> {name} <<<<<")
                print('')
                print('***** Testing Range *****')
                print('z: Skip Testing And Set MTU')
                print('y: MTU Pair Mode')
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
                    for line in interface_x:
                        confirm = input(f"Pair Interface {line} Y/N: ")
                        if confirm.lower() == 'y':
                            interface_list.append(line)
                            end_range1 = int(input('Max MTU Size: '))
                            work1 = list(range(start_range, (end_range1 + step_range), step_range))
                            device_list_work[line] = (work1)
                ip_source = next((a.address for a in psutil.net_if_addrs().get(name, []) if a.family == 2), None)
                iu = get_mtu(name, ipv)
                change_mtu(name, ipv, start_range)
                work = list(range(start_range, (end_range + step_range), step_range))
                admin_error = 1
                error1 = 0
                max_recheck = 0
                a = iu
                try:
                    while True:
                        if max_recheck > 4:
                            max_recheck = 0
                            number = num_max
                            if pair_mode == 1:
                                pair_mode_settings(name, b, ipv, n, interface_list, num_timestamp)
                        else:
                            number = random.choice(work)
                        print(f"{name} Trying: {number}")
                        b = change_mtu(name, ipv, number)
                        if pair_mode == 1:
                            for line in device_list_work:
                                xi = change_mtu(line, ipv, random.choice(device_list_work[line]))
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
                                    time.sleep(10)
                                    no_internet_boot()
                                    error1 == 1
                                continue
                            n = scoring(name, b, download, upload, ping)
                            if pair_mode == 1:
                                pair_mode_settings(name, b, ipv, n, interface_list)
                            num_max, num_timestamp = scoring_output(name, ipv)
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
