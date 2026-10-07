#python -m pip install python-nmap
#2026 Anthony R Shively (Mercer Ohio 1997)
import socket
import concurrent.futures
import ipaddress
import subprocess
import time
import re
import statistics
import psutil

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return (hostname,':', local_ip)

print(get_local_ip())  # e.g., '192.168.1.100'
print('')
#print(subprocess.run("ping 172.19.0.1", capture_output=True, text=True).stdout)
#time.sleep(5)
print('')
result = subprocess.run("ipconfig", shell=True, capture_output=True, text=True)
print(result.stdout)
print('')
out = subprocess.run("ipconfig", capture_output=True, text=True).stdout
ips = re.findall(r"IPv4 Address[.\s]*:\s*(\d+\.\d+\.\d+\.\d+)", out)

for ip in ips:
    print(f"\n--- Pinging {ip} ---")
    subprocess.run(f"ping -n 1 {ip}", shell=True)
def ping_once(ip):
    start = time.perf_counter()
    r = subprocess.run(f"ping -n 1 -w 1000 {ip}", shell=True,
                       capture_output=True, text=True)
    elapsed = (time.perf_counter() - start) * 1000   # ms
    up = r.returncode == 0
    return up, elapsed
print('1000x Pings')
for ip in ["172.19.0.1", "192.168.1.159", "192.168.1.170"]:
    up, ms = ping_once(ip)
    print(f"{ip:<18} {'UP  ' if up else 'DOWN'}  {ms:.2f} ms")
print('')
def tcp_probe(ip, port=445, timeout=1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    t = time.perf_counter()
    try:
        s.connect((ip, port))
        ok = True
    except ConnectionRefusedError:
        ok = True          # host responded
    except (socket.timeout, OSError):
        ok = False
    finally:
        ms = (time.perf_counter() - t) * 1000
        s.close()
    return ok, ms

def load_test(ip, port=445, count=100, workers=20):
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda _: tcp_probe(ip, port), range(count)))
    ok_times = [ms for ok, ms in results if ok]
    if not ok_times:
        return None
    return {
        "sent": count,
        "recv": len(ok_times),
        "loss": (count - len(ok_times)) / count * 100,
        "min": min(ok_times),
        "avg": statistics.mean(ok_times),
        "max": max(ok_times),
        "p95": sorted(ok_times)[int(len(ok_times) * 0.95)],
        "jitter": statistics.stdev(ok_times) if len(ok_times) > 1 else 0,
    }

for ip in ["172.19.0.1", "192.168.1.159", "192.168.1.170"]:
    print(f"\n=== {ip} ===")
    r = load_test(ip)
    if r:
        print(f"  Sent: {r['sent']}  Recv: {r['recv']}  Loss: {r['loss']:.1f}%")
        print(f"  min={r['min']:.2f}  avg={r['avg']:.2f}  max={r['max']:.2f}  "
              f"p95={r['p95']:.2f}  jitter={r['jitter']:.2f} ms")
print('')
'''def throughput_test(ip, port=445, duration=60):
    """Push data to a port for N seconds, measure MB/s."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((ip, port))
    except (ConnectionRefusedError, socket.timeout, OSError):
        print(f"{ip:<18} no service on port {port}")
        return

    chunk = b"x" * 65536   # 64 KB
    sent = 0
    start = time.time()
    try:
        while time.time() - start < duration:
            s.sendall(chunk)
            sent += len(chunk)
    except (socket.timeout, OSError):
        pass
    finally:
        elapsed = time.time() - start
        s.close()

    mbps = (sent * 8) / elapsed / 1_000_000
    print(f"{ip:<18} {sent/1e6:.1f} MB in {elapsed:.1f}s  =  {mbps:.1f} Mbps")

for ip in ["172.19.0.1", "192.168.1.159", "192.168.1.170"]:
    throughput_test(ip)'''
print('')
def measure(interval=2):
    old = psutil.net_io_counters(pernic=True)
    time.sleep(interval)
    new = psutil.net_io_counters(pernic=True)

    print(f"{'Interface':<22}{'Down (Mbps)':<14}{'Up (Mbps)'}")
    print("-" * 50)
    for iface in new:
        if iface in old:
            d = (new[iface].bytes_recv - old[iface].bytes_recv) * 8 / interval / 1e6
            u = (new[iface].bytes_sent - old[iface].bytes_sent) * 8 / interval / 1e6
            if d > 0 or u > 0:
                print(f"{iface:<22}{d:<14.3f}{u:.3f}")
measure(2)
print('')
try:
    print('DNS:', socket.gethostbyname("google.com"))
except socket.gaierror:
    print("DNS failed")
input('Exit Program')
