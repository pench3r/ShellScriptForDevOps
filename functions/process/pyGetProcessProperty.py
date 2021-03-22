#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
"""
Created by PyCharm.
File Name:              LinuxBashShellScriptForOps:pyGetProcessProperty.py
Version:                0.0.1
Author:                 Liuhongda
Author Email:           liuhongda@didiglobal.com
Create Date:            2018/2/2
Create Time:            14:45
Description:            get process's property(Name\Pid\Cpu ...) using psutil with python
Long Description:       
References:             
Prerequisites:          psutil
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
import psutil


def fn_timer(func):
    from functools import wraps

    @wraps(func)
    def function_timer(*args, **kwargs):
        import time
        time_begin = time.time()
        result = func(*args, **kwargs)
        time_end = time.time()
        print "Total time running {function_name}: {time_spent} seconds".format(function_name=func.func_name,
                                                                                time_spent=(time_end - time_begin))

        return result

    return function_timer


def get_pids(name):
    pid = set()
    if name:
        process_list = filter(lambda p: p.name().lower() == name.lower(), psutil.process_iter())
        # process_list2 = [process for process in psutil.process_iter() if process.name() == "Skype.exe"]

        for process in process_list:
            pid.add(process.pid)

    return list(pid)


if __name__ == '__main__':
    print get_pids("chrome.exe")

    proc = psutil.Process(pid=13544)
    print(proc.name())
    print(proc.cpu_percent(interval=1))
