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
from rich.progress import track
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
def scoring_output(name):
    try:
        #iox[tn] = ([name, mtu, download, upload, ping, score])
        iox = loads(f"{name}.json")
        iox_t = {}
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
        scores = [values[5] for values in iox.values()]
        max_score = max(scores)
        for line in iox:
            if max_score == iox.get(line)[5]:
                score_index = iox.get(line)
                print('Max MTU Score: ', line, score_index[0], score_index[1], score_index[2], score_index[3], score_index[4], score_index[5])
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
        return(b)
    except Exception as e:
        print('Changing MTU Issues:', e)
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
                print('0: Custom Value')
                print('1: IPV4 576 => 9014 (Jumbo Frame) Steps of 8')
                print('2: IPV4 576 => 9014 (Jumbo Frame) Steps of 1')
                print('3: IPV4 576 => 1500 (Standard Frame) Steps of 8')
                print('4: IPV4 576 => 1500 (Standard Frame) Steps of 1')
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
                elif a == '2':
                    ipv = 'IPV4'
                    step_range = 1
                    end_range = 9014
                    start_range = 576
                elif a == '4':
                    ipv = 'IPV4'
                    step_range = 1
                    end_range = 1500
                    start_range = 576
                elif a == '1':
                    ipv = 'IPV4'
                    step_range = 8
                    end_range = 9014
                    start_range = 576
                elif a == '3':
                    ipv = 'IPV4'
                    step_range = 8
                    end_range = 1500
                    start_range = 576
                iu = get_mtu(name, ipv)
                change_mtu(name, ipv, start_range)
                work = list(range(start_range, (end_range + 1), step_range))
                admin_error = 1
                a = iu
                try:
                    while True:
                        number = random.choice(work)
                        print(f"{name} Trying: {number}")
                        #a = get_mtu(name, ipv)
                        b = change_mtu(name, ipv, number)
                        #print(a, b, i)
                        if int(b) == int(number):
                            print(f"{name} {iu} Old: {a} => New: {b}")
                            download, upload, ping = speed_tester()
                            scoring(name, b, download, upload, ping)
                            #scoring(name, b, download, upload, ping)
                            #scoring(name, b, download, upload, ping)
                            scoring_output(name)
                            a = b
                        else:
                            if admin_error == 1:
                                print('Run As Admin')
                                admin_error = 0
                except KeyboardInterrupt:
                    print('Exited Loop')
                iu_x = change_mtu(name, ipv, iu)
        print('')
        input('Exit Program')
    except Exception as e:
        print('Main Issues:', e)
while True:
    main()
