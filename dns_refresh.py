#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import logging
import commands
import threading
from logging.handlers import RotatingFileHandler


logwd = '/data/proclog'
if not os.path.exists(logwd):
    os.makedirs(logwd)
logfile = '%s/dns_refresh.log' % logwd

logger = logging.getLogger('dnslogger')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - Thread:%(threadName)s - %(levelname)s - %(message)s')  
fh = RotatingFileHandler(logfile, maxBytes=20*1024*1024, backupCount=5)
fh.setFormatter(formatter)  
logger.addHandler(fh)

if (hasattr(os, "devnull")):
    NULL_DEVICE = os.devnull
else:
    NULL_DEVICE = "/dev/null"

def _redirectFileDescriptors():
    """
    redirect stdout and stderr.
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

def setdaemon():
    """
    make program run on daemon mode.
    """
    if os.name != 'posix':
        logger.critical('daemon is only supported on Posix-compliant systems.')
        os._exit(1)
    try:
        if(os.fork() > 0):
            os._exit(0)
    except OSError:
        logger.critical("create daemon failed.")
        os._exit(1)
    os.chdir('/')
    os.setsid()
    os.umask(0)
    try:
        if(os.fork() > 0):
            os._exit(0)
        _redirectFileDescriptors()
    except OSError:
        logger.critical("create daemon failed.")
        os._exit(1)

class per_dns_refresh_thread(threading.Thread):

    def __init__(self,domain,dns,interval,badtimes,threadName):
        threading.Thread.__init__(self, name=threadName)
        self.domain = domain
        self.dns = dns
        self.interval = interval 
        self.badtimes = badtimes

    def run(self):
        counter = initsize = self.badtimes
        errors = 0

        while True:
            logger.info("dns querying")
            cmd = 'dig %s @%s >/dev/null 2>&1' % (self.domain,self.dns)
            status = commands.getstatusoutput(cmd)[0]
            counter = counter -1
            if status:
                errors += 1

            if not counter:
                if errors == initsize:
                    logger.error(self.dns + " can't resolve " + self.domain + " destroy the thread.")
                    break
                else:
                    counter = initsize
                    errors = 0
            time.sleep(self.interval)


def cleandns(domains,dnss,retries):
    domains_dict = {}
    for d in domains:
        valid_dns = []
        for dns in dnss:
            cmd = 'dig +short +time=2 +tries=%s %s @%s >/dev/null 2>&1' % (retries,d,dns)
            status = commands.getstatusoutput(cmd)[0]
            if not status:
                valid_dns.append(dns)
            else:
                logger.error(dns + " can't resolve the " + d)
        domains_dict[d] = valid_dns
    return domains_dict

dnss = ['114.114.114.114','8.8.8.8','26.47.28.34','202.96.209.133','202.99.192.68',\
        '218.2.2.2','202.96.128.166','210.31.160.7','202.97.224.68','202.99.224.68',\
        '202.102.224.68','202.99.96.68','202.99.160.68']
domains = ['www.baidu.com','www.chinacache.com','www.126.com','www.163.com']
retries = 3 # retry times when judge if a dns is bad
interval = 0.1 # every domain-dns pair refresh interval 
badtimes = 60 # in a thread, if query badtimes continuous, destroy thread.

def generateTask():
    threads = []
    domains_dict = cleandns(domains,dnss,retries)
    for k, v in domains_dict.iteritems():
        for dns in v:
            threadName = k + "-by-" + dns
            t = per_dns_refresh_thread(k,dns,interval,badtimes,threadName)
            threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

if __name__ == '__main__':
    setdaemon()
    generateTask()

