#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
import socket
import sys
# import os
import time

host = ""
port = 0
timeout = 3
retry = 3


def usage():
    print("""
    Function: check remote host's tcp port if is open
    Usage: %s <host ipaddress> <tcp port>
    Example: python %s 127.0.0.1 22
    Others useful cli:
    strace time:
        strace -q -f -c python checkRemoteHostPortStatus.py 127.0.0.1 22
    Bash shell implement:
        nc -w 3 127.0.0.1 22 >/dev/null 2>&1 && echo ok || echo failed
        nmap 127.0.0.1 -p 22 | grep open >/dev/null 2>&1 && echo ok || echo failed

""") % (__file__, sys.argv[0])
    sys.exit(0)


argc = len(sys.argv)
if not (argc == 1 or argc == 3):
    print("Error: incorrect number of arguments or unrecognized option")
    usage()
if argc == 1:
    pass
else:
    if sys.argv[1] is not None:
        host = sys.argv[1]

    if sys.argv[2] is not None:
        try:
            port = int(sys.argv[2])
        except ValueError:
            pass

while True:
    if host == "":
        print "host is empty, please sign new one."
        host = raw_input("HOST: ")
    elif port == 0 or not isinstance(port, int):
        print "port is empty or illegal, please sign new one."
        try:
            port = int(raw_input("PORT: "))
        except ValueError:
            pass
    else:
        break

print "checking server %s port %s status." % (host, port)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(timeout)

for attempt in range(0, retry):
    try:
        s.connect((str(host), int(port)))
        print "connect to server %s port %s successfully!" % (host, port)
        break
    except Exception as e:
        print "connect to server %s port %s failed in %s times! " % (host, port, attempt + 1)
        # os.system("sleep 1")
        time.sleep(1)

s.close()
