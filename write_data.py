#!/usr/bin/env python 
from influxdb import InfluxDBClient
import time
import random
from datetime import datetime



writestart = time.time()

client = InfluxDBClient('localhost', 8086, 'root', 'root', 'thf_logger')
print("startup[ms]: " +str((time.time()-writestart)*1000))

writestart = time.time()

while 1:

    json_body = [

    ]
    dataset =     {
        "measurement": "example_dataset",
        "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "fields": {
            "current_l1":  random.random(),
            "current_l2":  random.random(),
            "current_l3":  random.random(),
            
            "voltage_l12":  random.random(),
            "voltage_l23":  random.random(),
            "voltage_l31":  random.random(),
            
            "voltage_temperature_l1":  random.random(),
            "voltage_temperature_l2":  random.random(),
            "voltage_temperature_l3":  random.random(),
            
            "voltage_aux":  random.random()
        }
    }
        
 #   dataset["fields"] = 
    json_body.append(dataset)
    
    writestart = time.time()
    client.write_points(json_body)
    print("writepoints[ms]: " +str((time.time()-writestart)*1000))
    
    time.sleep(1)

print("filling[ms]: " +str((time.time()-writestart)*1000))



#result = client.query('select current_l1 from example_dataset;')

#print("Result: {0}".format(result))