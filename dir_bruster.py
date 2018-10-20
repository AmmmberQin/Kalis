# -*- coding: utf-8 -*-
import os
import sys
import requests
import argparse
import threading
import queue
from urllib.parse import urljoin

def wordlists(wordlist_path):
    with open(wordlist_path, 'r') as f:
        for line in f.readlines():
            line = line.replace("\n","")
            yield line


def dir_bruster(target_url, words, extension, recurse):
    while not words.empty():
        attempt = words.get()
        target_attempt = urljoin(target_url, attempt)
        extension_attempts = [urljoin(target_url, f"{attempt}.{e}") for e in extension]

        for a in extension_attempts:
            r = requests.get(a)
            print(f"{r.status_code} => {a}")

        r = requests.get(target_attempt)
        print(f"{r.status_code} => {target_attempt}")
        if r.status_code == 200 and recurse:
            dir_bruster(target_attempt, words, extension, recurse)

def main(target_url, wordlist_path, thread, extension, recurse):
    words = queue.Queue()
    for w in wordlists(wordlist_path):
        words.put(w)
    
    for i in range(thread):
        t = threading.Thread(target=dir_bruster, args=(target_url, words, extension, recurse))
        t.start()


def parse_options():
    parser = argparse.ArgumentParser(usage='%(prog)s [options]',
                                     description='Dirbuster',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=
'''
Examples:
python dir_bruster.py -w '0.0.0.0' -t https://www.baidu.com
'''
                                        )
    parser.add_argument('-w','--wordlist', type=str, help='wordlist')
    parser.add_argument('-t','--thread', type=int, default=10, help='thread')
    parser.add_argument('-e','--extension',type=str, default="", help="expension")
    parser.add_argument('-r','--recurse', action="store_true", help='recursive')
    parser.add_argument('url', type=str, help='target url')
  
    args = parser.parse_args()

    if not os.path.exists(args.wordlist):
        print(f"[-] Error file in {args.wordlist} not exist")
        sys.exit(1)
    return args

if __name__ == "__main__":
    args = parse_options()
    if len(args.extension) == 0:
        extension = []
    else:
        extension = args.extension.split(",")

    main(args.url, args.wordlist, args.thread, extension, args.recurse)
