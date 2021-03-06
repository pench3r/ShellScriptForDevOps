#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created by PyCharm.
File Name:              LinuxBashShellScriptForOps:windows-user-accounts-manager.py
Version:                0.0.4
Author:                 dgden
Author Email:           liuhongda@didiglobal.com
Create Date:            2020/10/27
Create Time:            15:49
Description:            disable or enable Windows user account via WinRM remote commands
Long Description:

Enable-PSRemoting -Force
set firewall policy for TCP port 5985
telnet <server> 5985

Related Windows Services:
    WinRM: Windows Remote Management (WS-Management)

References:
Prerequisites:          pip install pywinrm
Development Status:     3 - Alpha, 5 - Production/Stable
Environment:            Console
Intended Audience:      System Administrators, Developers, End Users/Desktop
License:                Freeware, Freely Distributable
Natural Language:       English, Chinese (Simplified)
Operating System:       POSIX :: Linux, Microsoft :: Windows
Programming Language:   Python :: 2.6
Programming Language:   Python :: 2.7
Topic:                  Utilities
Notes:
 """
import json
import time
import warnings
from base64 import b64encode
from itertools import product
from multiprocessing import Pool

import requests
import winrm
from winrm.protocol import Protocol

# disable python warnings
warnings.filterwarnings("ignore")

BIZ_USERNAME_PREFIX = "biz name."
BIZ_EMPLOYEE_LIST = ['username 0', 'username 1', 'username 2', 'username 3']

with open("config.json") as fp:
    """
    {
      "self": {
        "1.1.1.1": {
          "account": "admin user",
          "password": "user password"
        },
      }
    }
    """
    config = json.load(fp)  # type: dict
    servers = config.get("self")  # type: dict


def get_ip_with_ends(num):
    """
    get full ip address with ip from config.json, ip num can be fourth part or full ip, such as '3' in '192.168.1.3'
    :param num: ip
    :type num: str | int
    :return: ip
    :rtype: str
    """
    if isinstance(num, int):
        num = str(num)

    if servers is not None:
        keys_list = servers.keys()
        for item in keys_list:  # type: str
            item = item.strip()
            if item.endswith(num):
                return item


def get_ip_with_ends_u1(num):
    """
    get full ip address with ip from config.json, ip num can be fourth part or full ip, such as '3' in '192.168.1.3'
    :param num: ip
    :type num: str | int
    :return: ip
    :rtype: str
    """
    if isinstance(num, int):
        num = str(num)

    if servers is None:
        raise KeyError("no servers is found")

    keys_list = servers.keys()
    keys_found_list = list()
    for item in keys_list:  # type: str
        item = item.strip()
        if item.endswith(num):
            keys_found_list.append(item)
    if len(keys_found_list) > 1:
        print("warning: more than one server is found, "
              "please use full ip addr instead last part.")
        return keys_found_list[0]
    elif len(keys_found_list) == 1:
        return keys_found_list[0]
    else:
        raise RuntimeError("no server is found, "
                           "please use full ip addr instead last part or check the config.json file.")


def get_acc_psw_with_ends(num):
    """
    get full ip address, username and password with given ip num from config.json
    :param num: ip
    :type num: str | int
    :return: ip_addr, account, password
    :rtype: tuple
    """
    if isinstance(num, int):
        num = str(num)

    ip_addr = get_ip_with_ends_u1(num)
    account = servers[ip_addr].get("account")
    password = servers[ip_addr].get("password")
    return ip_addr, account, password


def to_unicode_or_bust(obj, encoding='utf-8'):
    """
    convert non-unicode object to unicode object
    :param obj: str object or unicode
    :param encoding:
    :return:
    """
    import six
    if six.PY3:
        return obj

    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)

    return obj


def run_command_with_codepage(server, script, codepage=936):
    """
    [Chinese characters are not displayed properly #288](https://github.com/diyan/pywinrm/issues/288)
    [Code Page Identifiers](https://docs.microsoft.com/en-us/windows/win32/intl/code-page-identifiers)

    codepage use 936, gb2312, ANSI/OEM Simplified Chinese (PRC, Singapore); Chinese Simplified (GB2312)

    :param server:
    :type server:
    :param script:
    :type script:
    :param codepage:
    :type codepage:
    :return:
    :rtype:
    """
    ip, user, psw = get_acc_psw_with_ends(server)

    script = to_unicode_or_bust(script)
    encoded_ps = b64encode(script.encode('utf_16_le')).decode("ascii")

    p = Protocol(
        endpoint='http://{}:5985/wsman'.format(ip),
        transport='ntlm',
        username=user,
        password=psw)

    shell_id = p.open_shell(codepage=codepage)
    try:
        command_id = p.run_command(shell_id, 'powershell.exe', ['-EncodedCommand', encoded_ps])
        try:
            std_out, std_err, status_code = p.get_command_output(shell_id, command_id)
        finally:
            p.cleanup_command(shell_id, command_id)
    finally:
        p.close_shell(shell_id)

    print(std_out.decode('utf-8'))
    print(std_err.decode('utf-8'))
    print(status_code)

    return status_code, std_out, std_err


def run_powershell_with_codepage_936(target, username, password, script):
    """
    run remote command with WinRM

    [Chinese characters are not displayed properly #288](https://github.com/diyan/pywinrm/issues/288)
    [Code Page Identifiers](https://docs.microsoft.com/en-us/windows/win32/intl/code-page-identifiers)

    codepage use 936, gb2312, ANSI/OEM Simplified Chinese (PRC, Singapore); Chinese Simplified (GB2312)

    :param target: hostname or ip address
    :type target: str
    :param username:
    :type username: str
    :param password:
    :type password: str
    :param script: powershell commands or scripts
    :type script: str | unicode
    :return: status_code, std_out
    :rtype: tuple
    """
    script = to_unicode_or_bust(script)
    encoded_ps = b64encode(script.encode('utf_16_le')).decode("ascii")

    p = Protocol(
        endpoint='http://{}:5985/wsman'.format(target),
        transport='ntlm',
        username=username,
        password=password,
        read_timeout_sec=10,
        operation_timeout_sec=5,
    )

    try:
        shell_id = p.open_shell(codepage=936)
    except requests.exceptions.ConnectionError as e:
        return 1, "requests failed.", str(e)

    try:
        command_id = p.run_command(shell_id, 'powershell.exe', ['-EncodedCommand', encoded_ps])
        try:
            std_out, std_err, status_code = p.get_command_output(shell_id, command_id)
        finally:
            p.cleanup_command(shell_id, command_id)
    finally:
        p.close_shell(shell_id)

    # print(std_out.decode('utf-8'))
    # print(std_err.decode('utf-8'))
    # print(status_code)

    return status_code, std_out, std_err


def run_powershell(target, username, password, script):
    """
    run remote command with WinRM
    :param target: hostname or ip address
    :type target: str
    :param username:
    :type username: str
    :param password:
    :type password: str
    :param script: powershell commands or scripts
    :type script: str | unicode
    :return: status_code, std_out
    :rtype: tuple
    """
    shell = winrm.Session(target, auth=(username, password), transport="ntlm", read_timeout_sec=10,
                          operation_timeout_sec=5)

    script = to_unicode_or_bust(script)  # python2 using unicode here
    try:
        rs = shell.run_ps(script)
        # print rs.status_code, rs.std_out, rs.std_err
        return rs.status_code, rs.std_out, rs.std_err
    except requests.exceptions.ConnectionError as e:
        return 1, "requests failed.", str(e)


def disable_account(server, name):
    """
    disable user account
    :param server:hostname or ip address
    :type server:str | int
    :param name: user account name
    :type name:str
    :return:None
    :rtype:None
    """

    ip, user, psw = get_acc_psw_with_ends(server)
    if BIZ_USERNAME_PREFIX not in name:
        name = BIZ_USERNAME_PREFIX + name
    script = 'NET USER {name} /ACTIVE:NO'.format(name=name)
    # commenting the comments is for meeting the principle of 'Make each program do one thing well.'
    # print("disabling account {name} on {server}".format(name=name, server=ip))
    run_powershell(ip, user, psw, script)
    # print("account {} is disabled.".format(name))


def get_user_logged_on_server(server, name):
    """
    checkout if user is logged on the system, return False if fail or not logged on, True if logged on.
    quser.exe: Display information about users logged on to the system.

    :param server:hostname or ip address
    :type server:str | int
    :param name: user account name
    :type name:str
    :return:boolean
    :rtype:boolean
    """
    ip, user, psw = get_acc_psw_with_ends(server)
    if BIZ_USERNAME_PREFIX not in name:
        name = BIZ_USERNAME_PREFIX + name
    script = "[regex]::split(((quser.exe) -match '{name}'), '[ ]+')[3]".format(name=name)
    # commenting the comments is for meeting the principle of 'Make each program do one thing well.'
    # print("disabling account {name} on {server}".format(name=name, server=ip))
    status_code, std_out, std_err = run_powershell(ip, user, psw, script)
    if status_code != 0:
        return False
    else:
        if std_out.strip() in ["??????", "Disc"]:
            return False
        else:
            return True
    # print("account {} is disabled.".format(name))


def enable_account(server, name):
    """
    enable user account
    :param server:hostname or ip address
    :type server:str | int
    :param name: user account name
    :type name:str
    :return:None
    :rtype:None
    """
    ip, user, psw = get_acc_psw_with_ends(server)
    if BIZ_USERNAME_PREFIX not in name:
        name = BIZ_USERNAME_PREFIX + name
    script = 'NET USER {name} /ACTIVE:YES'.format(name=name)
    run_powershell(ip, user, psw, script)
    # commenting out this line is for meeting the principle of 'Make each program do one thing well.'
    # print("account {} is enabled.".format(name))


def query_account_status(server, name):
    """
    query user account status
    :param server:hostname or ip address
    :type server:str | int
    :param name: user account name
    :type name:str
    :return:Boolean
    :rtype:bool
    """
    ip, user, psw = get_acc_psw_with_ends(server)
    if BIZ_USERNAME_PREFIX not in name:
        name = BIZ_USERNAME_PREFIX + name
    script = '(Get-LocalUser -Name {name}).Enabled'.format(name=name)
    status_code, std_out, std_err = run_powershell(ip, user, psw, script)
    # $LastExitCode maybe 1, 2, etc, so do NOT use `status_code == 1`
    if status_code != 0:  # some reason: powershell version < 5.0
        # -Split (NET USER guest | where {$_ -match "????????????*"})| select -Last 1
        # (NET USER guest | where {$_ -match "????????????*"}).Split()[-1]
        # (NET USER guest | where {$_ -match "????????????*"}).Split()|select -Last 1
        # [bool]([regex]::Match(((NET USER guest) -match "????????????"),'Yes')).Success
        # [bool](((NET USER guest) -match "????????????") -match "no")
        script = '(NET USER {name} | where {{$_ -match "????????????*"}}).Split()|select -Last 1'.format(name=name)
        status_code, std_out, std_err = run_powershell_with_codepage_936(ip, user, psw, script)
        if status_code != 0:
            script = '[bool](((NET USER {name}) -match "????????????") -match "no")'.format(name=name)
            status_code, std_out, std_err = run_powershell_with_codepage_936(ip, user, psw, script)
            # print(std_out.strip())
            # print(std_err.strip())
            # if std_out in "requests failed.":
            #     print("WARN: account {} in IP {} may has an issue, "
            #           "such as `requests.exceptions.ConnectionError`, "
            #           u"error detail: {}.".format(name, ip, std_err.decode('gbk')))
            if "ConnectionError" in std_err:
                print("WARN: account {} in IP {} may has an issue, "
                      "such as `requests.exceptions.ConnectionError`, "
                      u"error detail: {}.".format(name, ip, std_err.decode('gbk')))
            return None

    status = std_out.strip()
    if status == "":
        status = "NotExist"
    # print("account {name}'s status on {server} is {status}.".format(name=name, status=status, server=server))
    return status in ["Yes", "True"]


def query_account_status_u1(server, name):
    """
    query user account status and return (account_status, message)
    status meaning:
        None: error, see message
        True: enabled
        False: disabled
    :param server:hostname or ip address
    :type server:str | int
    :param name: user account name
    :type name:str
    :return:tuple
    :rtype:tuple
    """
    ip, user, psw = get_acc_psw_with_ends(server)
    if BIZ_USERNAME_PREFIX not in name:
        name = BIZ_USERNAME_PREFIX + name
    script = '(Get-LocalUser -Name {name}).Enabled'.format(name=name)
    status_code, std_out, std_err = run_powershell(ip, user, psw, script)
    # $LastExitCode maybe 1, 2, etc, so do NOT use `status_code == 1`
    if status_code != 0:  # some reason: powershell version < 5.0
        # -Split (NET USER guest | where {$_ -match "????????????*"})| select -Last 1
        # (NET USER guest | where {$_ -match "????????????*"}).Split()[-1]
        # (NET USER guest | where {$_ -match "????????????*"}).Split()|select -Last 1
        # [bool]([regex]::Match(((NET USER guest) -match "????????????"),'Yes')).Success
        # [bool](((NET USER guest) -match "????????????") -match "no")
        script = '(NET USER {name} | where {{$_ -match "????????????*"}}).Split()|select -Last 1'.format(name=name)
        status_code, std_out, std_err = run_powershell_with_codepage_936(ip, user, psw, script)
        if status_code != 0:
            # print(std_out.strip())
            # print(std_err.strip())
            # if std_out in "requests failed.":
            #     print("WARN: account {} in IP {} may has an issue, "
            #           "such as `requests.exceptions.ConnectionError`, "
            #           u"error detail: {}.".format(name, ip, std_err.decode('gbk')))
            if "ConnectionError" in std_err:
                print("WARN: account {} in IP {} may has an issue, "
                      "such as `requests.exceptions.ConnectionError`, "
                      u"error detail: {}.".format(name, ip, std_err.decode('gbk')))
            return None, std_err

    message = std_out.strip()
    if message == "":
        message = "NotExist"

    account_status = message in ["Yes", "True"]
    # print("account {name}'s status on {server} is {status}.".format(name=name, status=status, server=server))
    return account_status, message


def main_change_account_status(ip=250, user='kurt'):
    print("exec time: {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))))
    is_account_enabled = query_account_status(ip, user)
    if is_account_enabled is True:
        # ?????????????????????????????????
        print("disabling account {name} on {server}".format(name=user, server=ip))
        disable_account(ip, user)
    elif is_account_enabled is False:
        # ?????????????????????????????????
        print("enabling account {name} on {server}".format(name=user, server=ip))
        enable_account(ip, user)
    else:
        print("status is strange, we should better verify it manually")

    account_status = query_account_status(ip, user)
    if account_status is None:
        print("status is strange, we should better verify it manually")
    elif account_status is True:
        print("account {name} on {server} is enabled.".format(name=user, server=ip))
    else:
        print("account {name} on {server} is disabled.".format(name=user, server=ip))


def main_change_account_status_u1(ip=250, user='kurt'):
    """

    :param ip:
    :type ip: str | int
    :param user:
    :type user:
    :return:
    :rtype:
    """
    import sys
    print("exec time: {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))))
    is_account_enabled, message = query_account_status_u1(ip, user)
    if is_account_enabled is True:
        # ?????????????????????????????????
        print("disabling account {name} on {server}".format(name=user, server=ip))
        disable_account(ip, user)
        account_status, message = query_account_status_u1(ip, user)
        if account_status is False:
            print("account {name} on {server} is disabled.".format(name=user, server=ip))
    elif is_account_enabled is False:
        # ?????????????????????????????????
        print("enabling account {name} on {server}".format(name=user, server=ip))
        enable_account(ip, user)
        account_status, message = query_account_status_u1(ip, user)
        if account_status is True:
            print("account {name} on {server} is enabled.".format(name=user, server=ip))
    else:
        print("status is strange, we should better verify it manually, message is: {msg}".format(msg=message))
        sys.exit(2)


def __main_disable_all_account():
    # deprecated
    if servers is not None:
        keys_list = servers.keys()
        for ip_addr in keys_list:  # type: str
            ip_addr = ip_addr.strip()
            print("DISABLING ACCOUNT ON {server}: ".format(server=ip_addr))
            for employee in BIZ_EMPLOYEE_LIST:
                is_account_enabled = query_account_status(ip_addr, employee)
                if is_account_enabled:
                    # ?????????????????????????????????
                    print("disabling account {name} on {server}".format(name=employee, server=ip_addr))
                    disable_account(ip_addr, employee)


def get_all_server_ip():
    server_ip_list = list()
    if servers is not None:
        keys_list = servers.keys()
        for ip_addr in keys_list:  # type: str
            ip_addr = ip_addr.strip()
            server_ip_list.append(ip_addr)

    return server_ip_list


def get_server_and_account_mapping():
    all_server_ip = get_all_server_ip()
    return list(product(all_server_ip, BIZ_EMPLOYEE_LIST))


def disable_account_wrapper(args):
    # use multiprocessing pool map with multiple-arguments
    # perhaps more pythonic: func = lambda x: func(*x) instead of defining a wrapper function
    # https://stackoverflow.com/questions/5442910/how-to-use-multiprocessing-pool-map-with-multiple-arguments

    # return disable_account(*args)

    ip, employee = args
    # print("DISABLING ACCOUNT ON {server}: ".format(server=ip))

    is_account_enabled = query_account_status(ip, employee)
    if is_account_enabled:
        # ?????????????????????????????????
        print("disabling account {name} on {server}".format(name=employee, server=ip))
        disable_account(ip, employee)


def main_disable_all_account():
    arguments_list = get_server_and_account_mapping()
    arguments_list = list(arguments_list)  # use list instead of generator type
    pool = Pool(processes=4)
    # pool.map(lambda x: disable_account(*x), arguments_list)
    pool.map(disable_account_wrapper, arguments_list)

    # TODO(DingGuodong) skip some users on some targets
    main_change_account_status(147, 'kurt')


if __name__ == '__main__':
    main_disable_all_account()
    # main_change_account_status_u1(147, 'username')
    # print get_user_logged_on_server(104, 'username')
