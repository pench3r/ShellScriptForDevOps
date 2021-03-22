#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
"""
Created by PyCharm.
File:               LinuxBashShellScriptForOps:catchException.py
User:               Liuhongda
Create Date:        2016/8/30
Create Time:        10:36
 """
import sys

import time

try:
    import os
    # raise SystemExit("raise SystemExit on purpose")
    # raise Exception("raise Exception on purpose")

except SystemExit, e:
    print(e)
    time.sleep(10)  # kill process here, finally statement will skipped
    print(e.args)
    print(e.message)
    sys.exit(1)
except Exception, e:
    sys.stderr.write(e.message + "\n")
    sys.exit(1)
else:
    print("no exceptions here, continue")

finally:
    print("always appear here")

print("exit now following 'else' statement")
