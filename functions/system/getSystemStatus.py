#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
"""
Created by PyCharm.
File:               LinuxBashShellScriptForOps:getSystemStatus.py
User:               Liuhongda
Create Date:        2016/8/18
Create Time:        15:32
 """
import os
import platform
import re
import subprocess
import sys

import prettytable
import psutil
import time

mswindows = (sys.platform == "win32")  # learning from 'subprocess' module
linux = (sys.platform == "linux2")


def get_local_ip():
    import netifaces
    routing_nic_name = netifaces.gateways()['default'][netifaces.AF_INET][1]
    for interface in netifaces.interfaces():
        if interface == routing_nic_name:
            try:
                routing_ip_addr = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
                return interface, routing_ip_addr
            except KeyError:
                pass


def get_user():
    if linux:
        proc_obj = subprocess.Popen(r'tty', shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        tty = proc_obj.communicate()[0]
    else:
        tty = []

    user_object = psutil.users()

    for login in user_object:
        try:
            username, login_tty, login_host, login_time = [suser for suser in login]
        except ValueError:  # different version
            # suser(name='Guodong', terminal=None, host='0.0.0.0', started=1511519014.0, pid=None)
            username, login_tty, login_host, login_time, pid = [suser for suser in login]
        print(username, login_tty, login_host, time.strftime('%b %d %H:%M:%S', time.localtime(login_time)),)
        if login_tty in tty:
            print('**current user**')
        else:
            print('')


def get_timezone():
    return time.strftime("%Z", time.gmtime())


def get_time_now():
    now = time.strftime('%a %b %d %H:%M:%S %Y %Z', time.localtime(time.time()))
    return now


def show_header():
    if linux:
        try:
            with open('/etc/issue') as f:
                content = f.read().strip()
                output_list = re.split(r' \\', content)
                linux_type = list(output_list)[0]
        except IOError:
            pass
        else:
            if linux_type is not None:
                return "Welcome to %s (%s %s %s)\n  System information as of %s" % (
                    linux_type, platform.system(), platform.release(), platform.machine(), get_time_now()
                )
            else:
                return
    if mswindows:
        def get_system_encoding():
            import codecs
            import locale
            """
            The encoding of the default system locale but falls back to the given
            fallback encoding if the encoding is unsupported by python or could
            not be determined.  See tickets #10335 and #5846
            """
            try:
                encoding = locale.getdefaultlocale()[1] or 'ascii'
                codecs.lookup(encoding)
            except Exception as _:
                del _
                encoding = 'ascii'
            return encoding

        DEFAULT_LOCALE_ENCODING = get_system_encoding()

        import _winreg
        try:
            reg_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion")
            if reg_key:
                ProductName = _winreg.QueryValueEx(reg_key, "ProductName")[0] or None
                EditionId = _winreg.QueryValueEx(reg_key, "EditionId")[0] or None
                ReleaseId = _winreg.QueryValueEx(reg_key, "ReleaseId")[0] or None
                BuildLabEx = _winreg.QueryValueEx(reg_key, "BuildLabEx")[0][:9] or None
                return "%s, %s [%s]\r\nVersion %s (OS Internal Version %s)" % (
                    ProductName, EditionId, platform.version(), ReleaseId, BuildLabEx)
        except Exception as e:
            print(e.message.decode(DEFAULT_LOCALE_ENCODING))


def get_hostname():
    return platform.node()


def get_cpu_percent():
    return [round(x / 100.0, 3) for x in psutil.cpu_percent(interval=0.1, percpu=True)]


def get_system_load():
    if linux:
        import multiprocessing
        k = 1.0
        k /= multiprocessing.cpu_count()
        if os.path.exists('/proc/loadavg'):
            return [float(open('/proc/loadavg').read().split()[x]) * k for x in range(3)]
        else:
            tokens = subprocess.check_output(['uptime']).split()
            return [float(x.strip(',')) * k for x in tokens[-3:]]
    if mswindows:
        # TODO(Guodong Ding) get this field data like on Linux for Windows
        # print(psutil.cpu_percent())
        # print(psutil.cpu_times_percent())
        # print(psutil.cpu_times())
        # print(psutil.cpu_stats())
        return "%.2f%%" % psutil.cpu_percent()


def get_memory():
    v = psutil.virtual_memory()
    return {
        'used': v.total - v.available,
        'free': v.available,
        'total': v.total,
        'percent': v.percent,
    }


def get_swap_memory():
    v = psutil.swap_memory()
    return {
        'used': v.used,
        'free': v.free,
        'total': v.total,
        'percent': v.percent
    }


def get_uptime():
    uptime_file = "/proc/uptime"
    if os.path.exists(uptime_file):
        with open(uptime_file, 'r') as f:
            return f.read().split(' ')[0].strip("\n")
    else:
        return time.time() - psutil.boot_time()


def get_uptime_u1():
    boot_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.boot_time()))
    print("system start at: %s" % boot_time,)
    uptime_total_seconds = time.time() - psutil.boot_time()
    uptime_days = int(uptime_total_seconds / 24 / 60 / 60)
    uptime_hours = int(uptime_total_seconds / 60 / 60 % 24)
    uptime_minutes = int(uptime_total_seconds / 60 % 60)
    uptime_seconds = int(uptime_total_seconds % 60)
    print("uptime: %d days %d hours %d minutes %d seconds" % (
        uptime_days, uptime_hours, uptime_minutes, uptime_seconds))

    user_number = len(psutil.users())
    print("%d user:" % user_number)
    print("  \\")
    for user_tuple in psutil.users():
        user_name = user_tuple[0]
        user_terminal = user_tuple[1]
        user_host = user_tuple[2]
        user_login_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(user_tuple[3]))
        print("  |- user online: %s, login from %s with terminal %s at %s" % (
            user_name, user_host, user_terminal, user_login_time))

    cpu_count = psutil.cpu_count()
    try:
        with open('/proc/loadavg', 'r') as f:
            loadavg_c = f.read().split(' ')
            loadavg = dict()
            if loadavg_c is not None:
                loadavg['lavg_1'] = loadavg_c[0]
                loadavg['lavg_5'] = loadavg_c[1]
                loadavg['lavg_15'] = loadavg_c[2]
                loadavg['nr'] = loadavg_c[3]
                loadavg['last_pid'] = loadavg_c[4]
        print("load average: %s, %s, %s" % (loadavg['lavg_1'], loadavg['lavg_5'], loadavg['lavg_15']))
        if float(loadavg['lavg_15']) > cpu_count:
            print("Note: cpu 15 min load is high!")
        if float(loadavg['lavg_5']) > cpu_count:
            print("Note: cpu 5 min load is high!")
        if float(loadavg['lavg_1']) > cpu_count:
            print("Note: cpu 1 min load is high!")
    except IOError:
        pass


if __name__ == '__main__':
    header = show_header()
    print(header)
    print('')

    system_load = str(get_system_load()).strip("[]")
    user_logged_in = len(psutil.users())
    info_of_root_partition = psutil.disk_usage("/")
    percent_of_root_partition_usage = "%.2f%%" % (
            float(info_of_root_partition.used) * 100 / float(info_of_root_partition.total))
    total_size_of_root_partition = "%.2f" % (float(psutil.disk_usage("/").total / 1024) / 1024 / 1024)
    memory_info = get_memory()
    memory_usage = "%.2f%%" % (float(memory_info['used']) * 100 / float(memory_info['total']))
    swap_info = get_swap_memory()
    swap_usage = "%.2f%%" % (float(swap_info['used']) * 100 / float(swap_info['total']))
    local_ip_address = get_local_ip()

    table = prettytable.PrettyTable(border=False, header=False, left_padding_width=2)
    table.field_names = ["key1", "value1", "key2", "value2"]
    table.add_row(["System load:", system_load, "Processes:", len(list(psutil.process_iter()))])
    table.add_row(["Usage of /:", "%s of %sGB" % (percent_of_root_partition_usage, total_size_of_root_partition),
                   "Users logged in:", user_logged_in])
    table.add_row(["Memory usage:", memory_usage, "IP address for %s:" % local_ip_address[0], local_ip_address[1]])
    table.add_row(["Swap usage:", swap_usage, "", ""])
    for field in table.field_names:
        table.align[field] = "l"

    print(table.get_string())
    print('')
    get_user()
    print('')
    get_uptime_u1()
