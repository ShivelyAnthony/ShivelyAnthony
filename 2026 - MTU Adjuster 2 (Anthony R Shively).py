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
from icmplib import ping
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
            for line_x in iox:
                if line == iox.get(line_x)[1]:
                    o_download.append(iox.get(line_x)[2])
                    o_upload.append(iox.get(line_x)[3])
                    o_ping.append(iox.get(line_x)[4])
                    o_score.append(iox.get(line_x)[5])
            iox_t[time.time()] = ([name, line, (sum(o_download) / len(o_download)), (sum(o_upload) / len(o_upload)), (sum(o_ping) / len(o_ping)), (sum(o_score) / len(o_score))])
        iox = iox_t
        dumps(f"{name}_avg.json", iox)
        download_scores = [values[2] for values in iox.values()]
        upload_scores = [values[3] for values in iox.values()]
        ping_scores = [values[4] for values in iox.values()]
        scores = [values[5] for values in iox.values()]
        max_download = max(download_scores)
        max_upload = max(upload_scores)
        min_ping = min(ping_scores)
        max_score = max(scores)
        for line in iox:
            if max_score == iox.get(line)[5]:
                score_index = iox.get(line)
            if min_ping == iox.get(line)[4]:
                ping_index = iox.get(line)
            if max_upload == iox.get(line)[3]:
                upload_index = iox.get(line)
            if max_download == iox.get(line)[2]:
                download_index = iox.get(line)
        print('MTU Max Download: ', download_index[0], download_index[1], download_index[2], download_index[3], download_index[4], download_index[5], all_mtus.count(download_index[1]))
        print('MTU Max Upload: ', upload_index[0], upload_index[1], upload_index[2], upload_index[3], upload_index[4], upload_index[5], all_mtus.count(upload_index[1]))
        print('MTU Lowest Ping: ', ping_index[0], ping_index[1], ping_index[2], ping_index[3], ping_index[4], ping_index[5], all_mtus.count(ping_index[1]))
        print('Max MTU Score: ', score_index[0], score_index[1], score_index[2], score_index[3], score_index[4], score_index[5], all_mtus.count(score_index[1]))
        ran_pick = [ping_index[1], score_index[1], upload_index[1], download_index[1]]
        if all_mtus.count(ping_index[1]) > 25:
            iop = change_mtu(name, ipv, ping_index[1])
            input('Program Finished: ', f"{name} {ping_index[1]}")
        elif all_mtus.count(score_index[1]) > 25:
            iop = change_mtu(name, ipv, score_index[1])
            input('Program Finished: ', f"{name} {score_index[1]}")
        return(random.choice(ran_pick))
    except Exception as e:
        print('Scoring Output Issues: ', e)
def scoring(name, mtu, download, upload, ping):
    iox = loads(f"{name}.json")
    score = (((download * .5) + (upload * .5)) / (ping))
    tn = time.time()
    iox[tn] = ([name, mtu, download, upload, ping, score])
    dumps(f"{name}.json", iox)
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
        return(download, upload, ping)
    except Exception as e:
        print('Speed Tester Issues:', e)
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
                ip_source = next((a.address for a in psutil.net_if_addrs().get(name, []) if a.family == 2), None)
                iu = get_mtu(name, ipv)
                change_mtu(name, ipv, start_range)
                work = list(range(start_range, (end_range + 1), step_range))
                admin_error = 1
                max_recheck = 0
                a = iu
                try:
                    while True:
                        if max_recheck > 4:
                            max_recheck = 0
                            number = num_max
                        else:
                            number = random.choice(work)
                        print(f"{name} Trying: {number}")
                        #a = get_mtu(name, ipv)
                        b = change_mtu(name, ipv, number)
                        #print(a, b, i)
                        if int(b) == int(number):
                            print(f"{name} {iu} Old: {a} => New: {b}")
                            python_ping(name, b, ip_source)
                            download, upload, ping = speed_tester()
                            scoring(name, b, download, upload, ping)
                            #scoring(name, b, download, upload, ping)
                            #scoring(name, b, download, upload, ping)
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
while True:
    main()
