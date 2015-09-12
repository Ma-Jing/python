# python
一些python的小脚本

## 1、dns_refresh.py

To keep some domain hot on specify local dns. 

Every valid domain-dns pair will create a thread.

When execute the script, the function setdaemon will fork a subprocess to run all threads, the main process will exit.


###Useage:

1. Edit the variable 'logfile' to store the error infomation.

2. Edit the list 'dnss' to specify the local dns.

3. Edit the domains to specify the domains you want to keep hot.

4. Edit the interval to specify the interval time for same domain-dns pair refresh.


## 2、ngxv2_traffic_daemon.py

提供一个指定域名实时流量的查询接口，可以通过zabbix或其他监控软件，实时监控域名的访问带宽和流量信息；

配置方法：

以监控www.test.com域名带宽为例；

1. 在web服务器上部署脚本，执行python nginx_traffic_daemon.py启动，启动后，脚本通过fork()的方式常驻后台；

2. 如该服务器已经部署zabbix_agentd，编辑zabbix_agentd.conf文件，添加一个自定义监控项
    UserParameter=nginx_channel_traffic[*],curl -s http://127.0.0.1:8888/$1 2>/dev/null

3. 在zabbix前端配置监控项目：
    + 监控项key: 为nginx_channel_traffic[www.test.com]
    + 数据类型：选择数字
    + 单位bps
    + 使用自定义倍数 8
    + 数据更新间隔: 300 (*可以根据实际情况修改*)
    + 储存值: 差量（每秒速率）
