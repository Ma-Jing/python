#!/usr/bin/env python
# -*- coding:utf-8 -*-
# a daemon which collecting channel traffic


import subprocess
import multiprocessing
import re
import os
import sys
import time
from os import stat
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

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
    """Make program run on daemon mode."""
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


logfile = '/data/www/access.log'
if not os.path.isfile(logfile):
    os._exit(1)

# ensure data is shared between every processes.
manager = multiprocessing.Manager()
channel_traffics = {}
channel_traffics = manager.dict()


# a log generator
def logtailer(logfile):
    ''' custom a generator, when logfile
    rotated, this generator will be closed'''
    with open(logfile) as f:
        last_inode = stat(logfile).st_ino
        f.seek(0, 2)  # seek to eof
        while True:
            line = f.readline()
            if not line:
                if last_inode != stat(logfile).st_ino:
                    raise StopIteration('logfile rotated')
                else:
                    time.sleep(0.05)
                    continue
            yield line


def analysis_and_format_log():
    sourcelines = logtailer(logfile)
    while True:
        try:
            line = sourcelines.next()
            channel, transfer_bytes = line.split()[0:11:10]
            if not transfer_bytes.isdigit():
                continue
            if channel_traffics.has_key(channel):
                channel_traffics[channel] += int(transfer_bytes)
            else:
                channel_traffics[channel] = int(transfer_bytes)
        except StopIteration, e:
            '''if log rotated, clear channel_traffics dict;
            then close old generator, start a new lines generator.'''
            sourcelines.close()
            channel_traffics.clear()
            sourcelines = logtailer(logfile)
        except Exception, e:
            continue #ignore other error.


class GetChannelBandHandler(BaseHTTPRequestHandler):
    '''a interface for query a channel current traffic'''
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
    server = ThreadedHTTPServer(("127.0.0.1", 8888), GetChannelBandHandler)
    print 'Starting server on 8888, use <Ctrl-C> to stop'
    server.serve_forever()
