#!/usr/bin/env python
# -*- coding:utf-8 -*-

import struct
import os
import socket

def query_codec(domain):
    index = os.urandom(2)
    #hoststr = r'\x0'.join(str(len(x)) + x for x in domain.split('.'))
    hoststr = ''.join(chr(len(x))+x for x in domain.split('.'))
    msg = b'\x5c\x6d\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00%s\x00\x00\x01\x00\x01' % hoststr
    #data = struct.pack(msg)
    return msg

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

msg = query_codec('www.baidu.com')

sock.sendto(msg,('8.8.8.8',53))

c = sock.recv(4096)
print c
