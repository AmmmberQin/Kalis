# -*- coding: utf-8 -*-
import sys
import re
import socket
import threading
import argparse

def handle_client(client_socket):
    request = client_socket.recv(1024)
    print(f"[*] Receving: {request}")
    client_socket.send(b"ACK!")
    client_socket.close()


def main(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5)

    print(f"[*] Listening on {ip}:{port}")
    while True:
        client, addr = server.accept()
        print(f"[*] Accepted connection from: {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

def parse_arguments():
    parser = argparse.ArgumentParser(description="SOCKET CLIENT")
    parser.add_argument('-i','--ip', default="localhost", type=str, help="host to listen")
    parser.add_argument('-p','--port', default=9999, type=int, help="port to listen")

    args = parser.parse_args()

    ip_pattern = "((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:(?<!\.)|\.)){4}"
    ip = re.match(ip_pattern, args.ip)
    valid_ip = (ip and ip.group(0) == args.ip)

    if not (args.ip == "localhost" or valid_ip):
        print("[-] ip is not valid. Exit...")
        sys.exit(1)

    if not (1000 < args.port <= 65535):
        print("[-] Invalid port number. Exiting")
        sys.exit(1)

    return args

if __name__ == '__main__':
    args = parse_arguments()
    main(args.ip, args.port)