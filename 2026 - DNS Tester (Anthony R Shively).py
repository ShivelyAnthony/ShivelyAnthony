#2026 Anthony R Shively (Mercer Ohio 1997)
import socket
import time
def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return (hostname,':', local_ip)
a, b, c = get_local_ip()
print(a, b, c)  # e.g., '192.168.1.100'
DNS_SERVER = c
DNS_PORT = 53

domains = [
    "www.youtube.com",
    "www.ancestry.com",
    "www.findagrave.com",
    "www.google.com",
]

def dns_query(domain):
    tid = int(time.time() * 1000) & 0xffff

    labels = domain.split(".")
    qname = b"".join(bytes([len(x)]) + x.encode() for x in labels) + b"\x00"

    packet = (
        tid.to_bytes(2, "big") +
        b"\x01\x00" +
        b"\x00\x01" +
        b"\x00\x00\x00\x00" +
        qname +
        b"\x00\x01" +
        b"\x00\x01"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    start = time.perf_counter()

    try:
        sock.sendto(packet, (DNS_SERVER, DNS_PORT))
        response, _ = sock.recvfrom(4096)
        elapsed = (time.perf_counter() - start) * 1000

        # DNS response code
        rcode = response[3] & 0x0F

        return True, elapsed, rcode, len(response)

    except Exception as e:
        return False, None, None, str(e)

    finally:
        sock.close()


print(f"Testing DNS server {DNS_SERVER}:{DNS_PORT}\n")

for domain in domains:
    ok, latency, rcode, result = dns_query(domain)

    if ok:
        status = {
            0: "NOERROR",
            1: "FORMERR",
            2: "SERVFAIL",
            3: "NXDOMAIN",
            5: "REFUSED",
        }.get(rcode, f"RCODE {rcode}")

        print(f"{domain:30} {status:10} {latency:7.1f} ms  {result} bytes")
    else:
        print(f"{domain:30} FAILED     {result}")
input('Exit Program')