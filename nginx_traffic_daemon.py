#!/usr/bin/env python
# -*- coding:utf-8 -*-
# a daemon which collecting channel traffic
# change log:
# * 2015.8.14: change 'tail -f' to 'tail -F' for avoiding logrotate interrupt

import subprocess
import multiprocessing
import re
import os
import sys
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

__authors__ = ['majing <majing@staff.sina.com.cn>']
__version__ = "1.1"
__date__ = "Aug 14, 2015"
__license__ = "GPL license"

if (hasattr(os, "devnull")):
    NULL_DEVICE = os.devnull
else:
    NULL_DEVICE = "/dev/null"


def _redirectFileDescriptors():
    """
    Redirect stdout and stderr.
    """
    import resource  # POSIX resource information
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = 1024

    for fd in range(0, maxfd):
        try:
            os.ttyname(fd)
        except:
            continue
        try:
            os.close(fd)
        except OSError:
            pass

    os.open(NULL_DEVICE, os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)


def python_daemon():
    """
    Make program run on daemon mode.
    """
    if os.name != 'posix':
        print 'Daemon is only supported on Posix-compliant systems.'
        os._exit(1)

    try:
        if(os.fork() > 0):
            os._exit(0)
    except OSError:
        print "create daemon failed."
        os._exit(1)

    os.chdir('/')
    os.setsid()
    os.umask(0)

    try:
        if(os.fork() > 0):
            os._exit(0)
        _redirectFileDescriptors()
    except OSError:
        print "create daemon failed."
        os._exit(1)


logfile = '/data0/log/sinaedge/esnv2/access.log'
if not os.path.isfile(logfile):
    os._exit(1)

# ensure data is shared between every processes.
manager = multiprocessing.Manager()
channel_traffics = {}
channel_traffics = manager.dict()


def analysis_and_format_log():
    command = 'tail -F ' + logfile
    tail_child = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    retcode = tail_child.poll()

    while retcode is None:
        line = tail_child.stdout.readline().strip()
        channel, transfer_bytes = line.split()[0:11:10]
        if not transfer_bytes.isdigit():
            transfer_bytes = 0
        if channel_traffics.has_key(channel):
            channel_traffics[channel] += int(transfer_bytes)
        else:
            channel_traffics[channel] = int(transfer_bytes)
        retcode = tail_child.poll()


class GetChannelBandHandler(BaseHTTPRequestHandler):
    ''' a interface for query a channel current traffic'''
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        query_channel = self.path.split('/')[-1]
        if query_channel in channel_traffics:
            current_traffic = channel_traffics[query_channel]
            self.wfile.write(current_traffic)
        else:
            self.wfile.write("404: channel not found")
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


if __name__ == "__main__":
    python_daemon()
    # start analysis_and_format_log function, run in backgroud.
    d = multiprocessing.Process(name='daemon', target=analysis_and_format_log)
    d.daemon = True
    d.start()
    server = ThreadedHTTPServer(("0.0.0.0", 8888), GetChannelBandHandler)
    print 'Starting server on 8888, use <Ctrl-C> to stop'
    server.serve_forever()
