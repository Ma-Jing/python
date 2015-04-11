# python
Python scripts that common use.

## 1、dns_refresh.py

To keep some domain hot on specify local dns. 

Every valid domain-dns pair will create a thread.

When execute the script, the function setdaemon will fork a subprocess to run all threads, the main process will exit.


###Useage:

(1) Edit the variable 'logfile' to store the error infomation.

(2) Edit the list 'dnss' to specify the local dns.

(3) Edit the domains to specify the domains you want to keep hot.

(4) Edit the interval to specify the interval time for same domain-dns pair refresh.


