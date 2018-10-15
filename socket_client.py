# -*- coding: utf-8 -*-
import sys
import re
import socket
import argparse

def udp_client(ip, port, data, file):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        if data:
            print(f"[*] Sending {data}")
            client.sendto(data.encode("utf-8"), (ip, port))
            data, addr = client_socket.recvfrom(4096)
            print(f"[*] Receving from {addr}...")
            print(data.decode("utf-8"))
        if file:
            print(f"[*] Sending file in path {file}")
            with open(file, "rb") as f:
                client_socket.sendto(f.read(), (ip, port))
            data, addr = client_socket.recvfrom(4096)
            print(f"[*] Receving from {addr}...")
            print(data.decode("utf-8"))


    except Exception as e:
        print(f"[-] UDP client failed: {e}")
        client_socket.close()

def tcp_client(ip, port, data, file):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip, port))
        if data:
            print(f"[*] Sending {data}")
            client_socket.send(data.encode("utf-8"))
            response = client_socket.recv(4096)
            print("[*] Receving...")
            print(response.decode("utf-8"))
        if file:
            print(f"[*] Sending file in path {file}")
            with open(file, "rb") as f:
                client_socket.send(f.read())
            response = client_socket.recv(4096)
            print("[*] Receving...")
            print(response.decode("utf-8"))
    except Exception as e:
        print(f"[-] TCP client failed: {e}")
        client_socket.close()

def parse_arguments():
    parser = argparse.ArgumentParser(description="SOCKET CLIENT")
    parser.add_argument('-t','--tcp', action="store_true", help="tcp mode")
    parser.add_argument('-u','--udp', action="store_true", help="udp mode")
    parser.add_argument('-i','--ip', default="localhost", type=str, help="host to listen")
    parser.add_argument('-p','--port', default=9999, type=int, help="port to listen")
    parser.add_argument('-d','--data', type=str, help="data to send")
    parser.add_argument('-f','--file', type=str, help="file path to be sent")

    args = parser.parse_args()

    if args.tcp | args.udp == 0:
        print("[-] must choice tcp or udp mode")
        sys.exit(1)

    ip_pattern = "((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:(?<!\.)|\.)){4}"
    ip = re.match(ip_pattern, args.ip)
    valid_ip = (ip and ip.group(0) == args.ip)

    if not (args.ip == "localhost" or valid_ip):
        print("[-] ip is not valid. Exit...")
        sys.exit(1)

    if not (1000 < args.port <= 65535):
        print("[-] Invalid port number. Exiting")
        sys.exit(1)

    if args.file is not None and not os.path.exists(args.file):
        print("[-] file not exist. Exit...")
        sys.exit(1)

    return args

if __name__ == "__main__":
    args = parse_arguments()
    if args.tcp:
        tcp_client(args.ip, args.port, args.data, args.file)
    elif args.udp:
        udp_client(args.ip, args.port, args.data, args.file)