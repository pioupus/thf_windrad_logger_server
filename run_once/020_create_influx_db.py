#!/usr/bin/env python 
from influxdb import InfluxDBClient
import os

my_env = os.environ.copy()    
DB_NAME = 'enerlyzer_logger'
                                                  
client = InfluxDBClient('localhost', 8086, 'root', 'root', DB_NAME)
client.create_user('admin', my_env["MY_PASSWORD"], admin=True)
client.create_user('influx_user', my_env["INFLUX_USER_PASSWORD"], admin=False)
client.create_database('enerlyzer')
