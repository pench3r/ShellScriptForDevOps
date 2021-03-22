#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
"""
Created by PyCharm.
File:               LinuxBashShellScriptForOps:pyConnectSQLServerWithpyodbc.py
User:               Liuhongda
Create Date:        2017/8/15
Create Time:        9:04
Description:        Python Connect to SQL Server on Windows With pyodbc
References:         Create Python apps using SQL Server on Windows
                    https://www.microsoft.com/en-us/sql-server/developer-get-started/python/windows/
                    https://www.microsoft.com/en-us/sql-server/developer-get-started/python/windows/step/2.html
                    See also, pymssql examples
                    http://pymssql.org/en/stable/pymssql_examples.html

 """
import pyodbc
from datetime import datetime

# https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Windows
driver = '{ODBC Driver 13 for SQL Server}'  # {ODBC Driver 13 for SQL Server} - supports SQL Server 2005 through 2016
server = 'localhost'
port = 1134
database = 'SampleDB'
username = 'sa'
password = 'your_password'
cnxn = pyodbc.connect(
    r'DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={password}'.format(
        driver=driver, server=server, port=port, database=database, username=username, password=password)
)

cursor = cnxn.cursor()

print ('Inserting a new row into table')
# Insert Query
tsql = "INSERT INTO Employees (Name, Location) VALUES (?,?);"
with cursor.execute(tsql, 'Jake', 'United States'):
    print ('Successfully Inserted!')

# Update Query
print ('Updating Location for Nikita')
tsql = "UPDATE Employees SET Location = ? WHERE Name = ?"
with cursor.execute(tsql, 'Sweden', 'Nikita'):
    print ('Successfully Updated!')

# Delete Query
print ('Deleting user Jared')
tsql = "DELETE FROM Employees WHERE Name = ?"
with cursor.execute(tsql, 'Jared'):
    print ('Successfuly Deleted!')

# Select Query
print ('Reading data from table')
tsql = "SELECT Name, Location FROM Employees;"
with cursor.execute(tsql):
    row = cursor.fetchone()
    while row:
        print (str(row[0]) + " " + str(row[1]))
        row = cursor.fetchone()

# Measure how long it takes to run the query
tsql = "SELECT SUM(Price) AS sum FROM Table_with_5M_rows"
a = datetime.now()
with cursor.execute(tsql):
    b = datetime.now()
    c = b - a
    for row in cursor:
        print ('Sum:', str(row[0]))
    print ('QueryTime:', c.microseconds, 'ms')
