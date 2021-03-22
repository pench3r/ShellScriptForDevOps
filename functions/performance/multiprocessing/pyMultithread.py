#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
"""
Created by PyCharm.
File Name:              LinuxBashShellScriptForOps:pyMultiprocessingExample.py
Version:                0.0.1
Author:                 Liuhongda
Author Email:           liuhongda@didiglobal.com
Download URL:           https://github.com/DingGuodong/LinuxBashShellScriptForOps/tarball/master
Create Date:            2017/11/13
Create Time:            14:39
Description:            using multiprocessing to run task on different CPU cores
Long Description:       The multiprocessing package offers both local and remote concurrency,
                        effectively side-stepping the Global Interpreter Lock by using subprocesses instead of threads.
                        Due to this, the multiprocessing module allows the programmer to
                        fully leverage multiple processors on a given machine. It runs on both Unix and Windows.
References:             
Prerequisites:          []
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
from itertools import repeat
from multiprocessing.pool import ThreadPool


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


def task(number):
    # an example of task takes long time
    import random
    return sorted([random.random() for _ in range(number)])


@fn_timer
def do_task_as_usual():
    for num in repeat(2000000, 8):
        task(num)


@fn_timer
def do_task_with_multithread():
    pool = ThreadPool(100)
    pool.map(task, repeat(2000000, 8))
    pool.close()
    pool.join()


if __name__ == '__main__':
    do_task_as_usual()  # Total time running do_task_as_usual: 19.6710000038 seconds
    do_task_with_multithread()  # Total time running do_task_with_multiprocessing: 9.64199995995 seconds
