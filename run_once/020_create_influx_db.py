#!/usr/bin/env python 
from influxdb import InfluxDBClient
import os

my_env = os.environ.copy()    
DB_NAME = 'enerlyzer'
                                                  
client = InfluxDBClient('localhost', 8086, 'root', 'root', DB_NAME)
client.create_user('admin', my_env["MY_PASSWORD"], admin=True)
client.create_user('influx_user', my_env["INFLUX_USER_PASSWORD"], admin=False)
client.create_user('influx_reader', my_env["INFLUX_READER_PASSWORD"], admin=False)
client.create_database(DB_NAME)
client.grant_privilege('ALL', DB_NAME, 'influx_user')
client.grant_privilege('READ', DB_NAME, 'influx_reader')
