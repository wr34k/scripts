#!/usr/bin/python3

import sys
import time
import requests
import socket
from argparse import ArgumentParser

proxy_list = dict()
throttle=0.5
def main():

    args = getargs()
    last_i = 0
    i=1
    types=list()

    if not args.socks5 and not args.socks4 and not args.http:
            print("[!] Error! Please select at least one protocol...")
            return

    if args.socks5:
        types.append("socks5")
    if args.socks4:
        types.append("socks4")
    if args.http:
        types.append("http")

    while True:
        if i > args.count:
            break
        if i > last_i:
            print(f"[*] Getting proxy num {i}...")
        last_i = i
        time.sleep(throttle)
        r = requests.get("https://gimmeproxy.com/api/getProxy")
        ret = r.json()
        print(ret)


        if 'protocol' in ret:
            if (ret['protocol'] in types):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((ret['ip'], int(ret['port'])))
                    s.close()
                except:
                    print("[x] Proxy not responding...")
                    continue

                if not ret['protocol'] in proxy_list:
                    proxy_list[ret['protocol']] = list()
                proxy_list[ret['protocol']].append( (ret['ip'], ret['port'], ret['country']) )
                i+=1


    for proto in proxy_list:
            print(f"-- {proto} --")
            for proxy in proxy_list[proto]:
                print(f"{proto} {proxy[0]} {proxy[1]} # {proxy[2]}")
            print("")

    if args.output:
        with open(args.output, "w") as f:
            for proto in proxy_list:
                f.write(f"# {proto}\n")
                for proxy in proxy_list[proto]:
                    f.write(f"{proto} {proxy[0]} {proxy[1]} # {proxy[2]}\n")


def getargs():
    p = ArgumentParser()
    p.add_argument("-c", "--count", help="How many proxies to fetch", default=10, type=int)
    p.add_argument("-s5", "--socks5", help="Getting socks5 proxies", action="store_true", default=False)
    p.add_argument("-s4", "--socks4", help="Getting socks4 proxies", action="store_true", default=False)
    p.add_argument("-ht", "--http", help="Getting http proxies", action="store_true", default=False)
    p.add_argument("-o", "--output", help="Output to file")

    return p.parse_args()


if __name__=='__main__':
    main()
