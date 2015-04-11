# python
Python script that common use

## 1、dns_refresh.py

To keep some domain hot on specify local dns. 

Every valid domain-dns pair will create a thread.

When execute the script, the function setdaemon will fork a subprocess to run all threads, the main process will exit.


###Useage:

(1) edit the variable "logfile" to store the error infomation.

(2) edit the list "dnss" to specify the local dns.

(3) edit the domains to specify the domains you want to keep hot.

(4) edit the interval to specify the interval time for same domain-dns pair refresh.


