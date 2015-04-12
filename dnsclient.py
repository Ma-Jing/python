#!/usr/bin/env python
# -*- coding:utf-8 -*-

import struct
import os
import socket

def query_codec(domain):
    index = os.urandom(2)
    hoststr = ''.join(chr(len(x)) + x for x in domain.split('.'))
    print hoststr
    data = '%s\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00%s\x00\x00\x01\x00\x01' % (index, hoststr)
    data = struct.pack('!H', len(data)) + data
    return data

def resp_decode(in_sock):
    rfile = in_sock.makefile('rb')   
    size = struct.unpack('!H', rfile.read(2))[0]
    data = rfile.read(size)
    iplist = re.findall('\xC0.\x00\x01\x00\x01.{6}(.{4})', data)
    print ['.'.join(str(ord(x)) for x in s) for s in iplist]


sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

sock.connect(('114.114.114.114',53))
msg = query_codec('www.baidu.com')

sock.sendall(msg)
print sock.recv(4096)
print resp_decode(sock)
