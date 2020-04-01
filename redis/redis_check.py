# -*- coding: UTF-8 -*-
# !/usr/bin/env python

'''
Zabbix ddl for redis
@version: 1.0
@date: 2020.03.18
@author:wyj 
'''
import commands
import socket
import fcntl
import struct
import re
import sys


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def check_redis(password, check_items, item):
    passowrd = password
    command = "ifconfig |grep -v \"127.0.0.1\" |head -n 1|awk -F \":| \" '{print $1}'"
    stat, results = commands.getstatusoutput(command)
    ip = get_ip_address(results)
    command = "cd /opt/redis-3.2.4;./redis-cli -h " + ip + " -a '" + password + "' info " + check_items
    stat, results = commands.getstatusoutput(command)
    temp = re.split(r'(\r\n|:|\r)', results)[::2][1:]
    data = {}
    i = 0 
    while i < len(temp)-1:
        data[temp[i]] = temp[i+1]
        i = i + 2
#    print(data["used_memory"])
#    print(data["total_system_memory"])
    if check_items == "MEMORY":
        data["useage_memory"] = float(data["used_memory"])/float(data["total_system_memory"])
        return(float(data[item]))
    elif check_items == "Stats":
        return(float(data[item]))
    elif check_items == "CPU":
        return(float(data[item]))
    else:
        if data[item] == "up":
            return 1
        else:
            return 0

if __name__ == "__main__":
       command = "cat /opt/redis-3.2.4/redis.conf|grep '^requirepass'|awk '{print $2}'" 
       stat, password = commands.getstatusoutput(command)
       item_type = sys.argv[1]
       item = sys.argv[2]
       print(check_redis(password, item_type, item))
