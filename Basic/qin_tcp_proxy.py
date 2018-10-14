# -*- coding: utf-8 -*-
import sys
import socket
import threading
import argparse

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2

    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = "".join(["{:0{}b}".format(x, digits) for x in s])
        text = "".join([x.decode("utf-8") if 0x20 <= a[0] < 0x7f else "." for x in s])
        result.append("{:4} - {}".format(text, hexa))

    print "\n".join(result)

def receive_from(connection):
    buf = b""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buf += data
    except:
        pass
    return buf

def request_handler(buf):
    return buf

def response_handler(buf):
    return buf
        
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_socket.connect((remote_host, remote_port))
        if receive_first:
            remote_buffer = receive_from(remote_socket)
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            if len(remote_buffer):
                print(f"[<==] Sending {len(remote_buffer)} bytes to localhost.")
                client_socket.send(remote_buffer)
        
        while True:
            local_buffer = receive_from(client_socket)
            if len(local_buffer):
                print(f"[==>] Received {len(local_buffer)} bytes from localhost.")
                hexdump(local_buffer)
                local_buffer = request_handler(local_buffer)

                remote_socket.send(local_buffer)
                print(f"[==>] Send to remote")

            remote_buffer = receive_from(remote_socket)

            if len(remote_buffer):
                print(f"[<==] Received {len(remote_buffer)} from remote.")
                hexdump(remote_buffer)

                remote_buffer = response_handler(remote_buffer)

                client_socket.send(remote_buffer)

                print(f"[<==] Sent to localhost")
            if len(local_buffer) == 0 or len(remote_buffer) == 0:
                client_socket.close()
                remote_socket.close()
                print("[*] No more data. Closing connections")
                break
                
    except Exception as e:
        print(f"[-] Error: {e}")
        remote_socket.close()
        client_socket.close()


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
        server.listen(5)

        while True:
            client_socket, addr = server.accept()
            print(f"Received incoming connection from {addr[0]}:{addr[1]}")
            proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket,remote_host,remote_port,receive_first))
            proxy_thread.start()
    except Exception as e:
        print(f"[-] Error: {e}")
        server.close()

def parse_arguments():
    parser = argparse.ArgumentParser(description="FAKE NETCAT")
    parser.add_argument('-l','--local_host', default="localhost", type=str, help="local host")
    parser.add_argument('-p','--local_port', type=int, help="local port")
    parser.add_argument('-r','--remote_host', type=str, help="remote host")
    parser.add_argument('-t','--remote_port', type=int, help="remote port")
    parser.add_argument('-f','--receive_first', action="store_true")
    
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arguments()
    server_loop(args.local_host, args.local_port, args.remote_host, args.remote_port, args.receive_first)


