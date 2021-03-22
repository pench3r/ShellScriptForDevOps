#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
"""
Created by PyCharm.
File:               LinuxBashShellScriptForOps:getLinuxDist.py
User:               Liuhongda
Create Date:        2017/3/9
Create Time:        10:07
 """
import sys

mswindows = (sys.platform == "win32")  # learning from 'subprocess' module
linux = (sys.platform == "linux2")


def _win_or_linux():
    # os.name ->(sames to) sys.builtin_module_names
    if 'posix' in sys.builtin_module_names:
        os_type = 'Linux'
    elif 'nt' in sys.builtin_module_names:
        os_type = 'Windows'
    return os_type


def is_windows():
    if "windows" in _win_or_linux().lower():
        return True
    else:
        return False


def is_linux():
    if "linux" in _win_or_linux().lower():
        return True
    else:
        return False


def is_debian_family():
    import platform
    # http://stackoverflow.com/questions/2988017/string-comparison-in-python-is-vs
    # http://stackoverflow.com/questions/1504717/why-does-comparing-strings-in-python-using-either-or-is-sometimes-produce
    if platform.system() == "Linux":
        distname = platform.linux_distribution()
        if "Ubuntu" in distname or "Debian" in distname:
            return True
        else:
            return False
    else:
        return False


def is_rhel_family():
    import platform
    if platform.system() == "Linux":
        distname = platform.linux_distribution()
        if "CentOS" in distname or "Debian" in distname:
            return True
        else:
            return False
    else:
        return False
