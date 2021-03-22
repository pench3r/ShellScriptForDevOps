#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
"""
Created by PyCharm.
File:               LinuxBashShellScriptForOps:resetPrinterSpoolerService.py
User:               Liuhongda
Create Date:        2017/9/7
Create Time:        15:07
Description:        reset Windows printer spooler service to make printers work again
References:
Prerequisites:      pypiwin32: pip install pypiwin32
                    Optional: install 'pywin32'
 """
import os
import sys
import time

import win32service
import win32serviceutil


def get_system_encoding():
    """
    The encoding of the default system locale but falls back to the given
    fallback encoding if the encoding is unsupported by python or could
    not be determined.  See tickets #10335 and #5846
    """
    import codecs
    import locale

    try:
        encoding = locale.getdefaultlocale()[1] or 'ascii'
        codecs.lookup(encoding)
    except Exception as _:
        del _
        encoding = 'ascii'
    return encoding


def reset_printer():
    """
    Note: administrator privilege is required

    this function do three things:
    1. stop Print Spooler service
    2. delete all job files
    3. start Print Spooler service
    :return:
    """
    service_name = 'spooler'.capitalize()
    win_dir = os.environ.get('windir', r'C:\Windows')
    printer_path = r"System32\spool\PRINTERS"
    path = os.path.join(win_dir, printer_path)

    status_code_map = {
        0: "UNKNOWN",
        1: "STOPPED",
        2: "START_PENDING",
        3: "STOP_PENDING",
        4: "RUNNING"
    }

    DEFAULT_LOCALE_ENCODING = get_system_encoding()

    print "printer spool folder is: %s" % path

    if os.path.exists(path):
        if os.listdir(path):
            print "reset printer spooler service in progress ..."

            status_code = win32serviceutil.QueryServiceStatus(service_name)[1]
            if status_code == win32service.SERVICE_RUNNING or status_code == win32service.SERVICE_START_PENDING:
                print "stopping service {service}".format(service=service_name)
                win32serviceutil.StopService(serviceName=service_name)

            # waiting for service stop, in case of WindowsError exception
            # 'WindowsError: [Error 32]' which means
            # 'The process cannot access the file because it is being used by another process'.
            running_flag = True
            while running_flag:
                print "waiting for service {service} stop.".format(service=service_name)
                status_code = win32serviceutil.QueryServiceStatus(service_name)[1]
                time.sleep(2)
                if status_code == win32service.SERVICE_STOPPED:
                    running_flag = False

            for top, dirs, nondirs in os.walk(path, followlinks=True):
                for item in nondirs:
                    path_to_remove = os.path.join(top, item)
                    try:
                        os.remove(path_to_remove)
                    except WindowsError:
                        time.sleep(2)
                        r""" KNOWN ISSUE:
                        It will also can NOT remove some files in some Windows, such as 'Windows Server 2012'
                        Because file maybe used by a program named "Print Filter Pipeline Host",
                        "C:\Windows\System32\printfilterpipelinesvc.exe"
                        It will throw out  'WindowsError: [Error 32]' exception again.
                        """
                        os.remove(path_to_remove)
                    except Exception as e:
                        print e
                        print e.args
                        print e.message
                    print "file removed: {file}".format(file=path_to_remove)

            status_code = win32serviceutil.QueryServiceStatus(service_name)[1]
            if status_code != win32service.SERVICE_RUNNING and status_code != win32service.SERVICE_START_PENDING:
                print "starting service {service}".format(service=service_name)
                win32serviceutil.StartService(serviceName=service_name)
        else:
            print "current printer spooler in good state, skipped."
    else:
        print "Error: {path} not found, system files broken!".format(path=path)
        sys.exit(1)

    status_code = win32serviceutil.QueryServiceStatus(service_name)[1]
    if status_code == win32service.SERVICE_RUNNING or status_code == win32service.SERVICE_START_PENDING:
        print "[OK] reset printer spooler service successfully!"
    else:
        print "current service code is {code}, and service state is {state}.".format(code=status_code,
                                                                                     state=status_code_map[status_code])
        try:
            print "trying start spooler service..."
            win32serviceutil.StartService(serviceName=service_name)
            status_code = win32serviceutil.QueryServiceStatus(service_name)[1]
            if status_code == win32service.SERVICE_RUNNING or status_code == win32service.SERVICE_START_PENDING:
                print "service {service} started.".format(service=service_name)
        except Exception as e:
            print e
            print [msg.decode(DEFAULT_LOCALE_ENCODING) for msg in e.args]
            print e.message.decode(DEFAULT_LOCALE_ENCODING)


if __name__ == '__main__':
    reset_printer()
