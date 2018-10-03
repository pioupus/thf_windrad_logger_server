#!/usr/bin/env python 

import os
import time
import sys
from datetime import datetime
import paho.mqtt.client as mqtt
import protobuf_logger_pb2

broker="broker.hivemq.com"
INFLUX_DB_NAME = "enerlyzer"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("enerlyzer/#")

def on_message(client, userdata, msg):
    msg_hex = [elem.encode("hex") for elem in msg.payload]
    #print(msg.topic + " " + str(msg_hex))
    print("length: "+str(len(msg_hex)))
    protobuf_dataset = protobuf_logger_pb2.dataset()
    protobuf_dataset.ParseFromString(msg.payload)
    print(protobuf_dataset)
     
    
    influx_data_set =     [{
        "measurement": "powerdata",
        "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        "fields": {
            "logger_time":      protobuf_dataset.logger_time,
            "current_l1_avg":  protobuf_dataset.current_l1_avg,
            "current_l2_avg":  protobuf_dataset.current_l2_avg,
            "current_l3_avg":  protobuf_dataset.current_l3_avg,
            
            "voltage_l21_avg":  protobuf_dataset.voltage_l21_avg,
            "voltage_l32_avg":  protobuf_dataset.voltage_l32_avg,
            "voltage_l13_avg":  protobuf_dataset.voltage_l13_avg,
            
            "current_l1_eff":  protobuf_dataset.current_l1_eff,
            "current_l2_eff":  protobuf_dataset.current_l2_eff,
            "current_l3_eff":  protobuf_dataset.current_l3_eff,
            
            "voltage_l21_eff":  protobuf_dataset.voltage_l21_eff,
            "voltage_l32_eff":  protobuf_dataset.voltage_l32_eff,
            "voltage_l13_eff":  protobuf_dataset.voltage_l13_eff,

            "current_l1_max":  protobuf_dataset.current_l1_max,
            "current_l2_max":  protobuf_dataset.current_l2_max,
            "current_l3_max":  protobuf_dataset.current_l3_max,
            
            "voltage_l21_max":  protobuf_dataset.voltage_l21_max,
            "voltage_l32_max":  protobuf_dataset.voltage_l32_max,
            "voltage_l13_max":  protobuf_dataset.voltage_l13_max,
            
            "temperature_l1":  protobuf_dataset.temperature_l1,
            "temperature_l2":  protobuf_dataset.temperature_l2,
            "temperature_l3":  protobuf_dataset.temperature_l3,
            
            "voltage_aux":  protobuf_dataset.voltage_aux,
            
            "frequency_Hz":  protobuf_dataset.frequency_Hz,
            "power":  protobuf_dataset.power,
            "external_current_sensor":  protobuf_dataset.external_current_sensor,
            
            "supply_voltage":  protobuf_dataset.supply_voltage,
            "cpu_temperature":  protobuf_dataset.cpu_temperature,
            "coin_cell_mv":  protobuf_dataset.coin_cell_mv,
            "energy_Wh": protobuf_dataset.energy_Wh,
            "energy_start": protobuf_dataset.energy_acquisition_start,
            "used_storage_percent:": protobuf_dataset.used_storage_percent
            
        }
    }]
        
    influx_client.write_points(influx_data_set)
    


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


my_env = os.environ.copy()    
influx_client = InfluxDBClient('localhost', 8086, 'influx_user', my_env["INFLUX_USER_PASSWORD"], INFLUX_DB_NAME)
#influx_client = InfluxDBClient('localhost', 8086, 'influx_user', "", INFLUX_DB_NAME)

mqtt_publish_result = mqtt_client.publish("enerlyzer/live/pwr", "test", qos=2)
print(mqtt_publish_result)
if mqtt_publish_result.rc == mqtt.MQTT_ERR_SUCCESS:
    print("published successfully")
    
if mqtt_publish_result.rc == mqtt.MQTT_ERR_NO_CONN:
    print("Not connected")    
    mqtt_client.connect(broker, 1883, 60)
mqtt_client.loop_forever()
