#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created by PyCharm.
File Name:              LinuxBashShellScriptForOps:get-time-from-ntp-server.py
Version:                0.0.1
Author:                 dgden
Author Email:           liuhongda@didiglobal.com
Download URL:           https://github.com/DingGuodong/LinuxBashShellScriptForOps/tarball/master
Create Date:            2020/7/2
Create Time:            10:52
Description:            get time from ntp server
Long Description:       python -c "import ntplib;from time import ctime;print(ctime(ntplib.NTPClient().request('pool.ntp.org').tx_time))"
References:             
Prerequisites:          sudo -H pip install ntplib
Development Status:     3 - Alpha, 5 - Production/Stable
Environment:            Console
Intended Audience:      System Administrators, Developers, End Users/Desktop
License:                Freeware, Freely Distributable
Natural Language:       English, Chinese (Simplified)
Operating System:       POSIX :: Linux, Microsoft :: Windows
Programming Language:   Python :: 2.6
Programming Language:   Python :: 2.7
Topic:                  Utilities
 """
import ntplib
import time
from time import ctime

c = ntplib.NTPClient()

response = None

try:
    response = c.request('pool.ntp.org')
except ntplib.NTPException as e:
    print(e)
except Exception as e:
    print(e)

if response:
    print("current offset time: {}".format(response.offset))
    print("current server time: {}".format(ctime(response.tx_time)))
    print("current system time: {}".format(ctime()))
    print("current system time: {}".format(time.strftime("%a %b %d %H:%M:%S %Y")))
