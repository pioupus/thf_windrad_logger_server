#!/usr/bin/env python 
import subprocess
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
import time
import os
import json
import sys
from datetime import datetime
import random
import socket
import protobuf_logger_pb2
import paho.mqtt.client as mqtt
from decimal import Decimal
import os


BROKER="broker.hivemq.com"
INFLUX_DB_NAME = "enerlyzer"+datetime.now().strftime("%Y_%m-%d_%H_%M_%S")

def mqtt_result_numer_to_string(rc):
    if rc == 0:
        return "Connection successfull("+str(rc)+")"
    if rc == 1:
        return "Connection refused - incorrect protocol version("+str(rc)+")"
    if rc == 2:
        return "Connection refused - invalid client identifier("+str(rc)+")"
    if rc == 3:
        return "Connection refused - server unavailable("+str(rc)+")"
    if rc == 4:
        return "Connection refused - bad username or password("+str(rc)+")"
    if rc == 4:
        return "Connection refused - not authorised("+str(rc)+")"      
    return "Currently unused error code("+str(rc)+")"  
    
def string_to_ord(text,length):
    result = []
    for char in text:
        result.append(ord(char))
    for i in range(len(result),length):
        result.append(0)
    return result

def mqtt_on_disconnect(client, userdata, flags, rc):
    print("MQTT disconnected. Result: "+mqtt_result_numer_to_string(rc))
    print("try to reconnect..")
    client.reconnect()
     
def mqtt_on_connect(client, userdata, flags, rc):
    print("MQTT connected. Result: "+mqtt_result_numer_to_string(rc))  
     
class RPCProtocol:
    def __init__(self, comport_path, baud, xml_search_dir):
        my_env = os.environ.copy()
        #my_env["LD_LIBRARY_PATH"] = "/home/pi/JSONtoRPCbridge/bin/release"

        self.rpc_json_bridge_process = subprocess.Popen([my_env["THF_LOGGER_RPC_BIN"], comport_path, str(baud), xml_search_dir], env=my_env, cwd=r'../', stdin=subprocess.PIPE,stdout=subprocess.PIPE, shell = False)
        self._start_tag_positions = []
        self._stop_tag_positions = []




    def _test_json_input(self, test_str):
        result = True
        test_str = test_str[2:-2];                # remove the / of the /{
        
        #print("test_str: "+test_str)
        decoded_answer = {}
        try:
            decoded_answer = json.loads(test_str, parse_int=Decimal, parse_float=Decimal)
            
        except ValueError:
            result = False
        
        rpc = {"success": result, "answer":decoded_answer}
        
        return rpc
    

        

    def _append_answer_byte(self, character):
        self._input_buffer += character
        input_not_empty = True
        finished = False
        decoded_answer = {}
        count = 0;
        duration_position_time = 0;
        duration_stop_tag_time = 0;
        duration_start_tag_time = 0;

        while input_not_empty:

            found = False
            
            if self._input_buffer.endswith("/{"):
                self._start_tag_positions.append(len(self._input_buffer)-2);
            

            if self._input_buffer.endswith("}/"):
                self._stop_tag_positions.append(len(self._input_buffer)-2);

            positions_tag_time = time.clock()
            if self._input_buffer.endswith("}/"):
                for start in self._start_tag_positions:

                    for stop in self._stop_tag_positions:
                        if stop < start:
                            continue
                        test_str = self._input_buffer[start : stop  + len('}/')]
                        rpc_result = self._test_json_input(test_str)
                        if rpc_result["success"]:
                            self._input_buffer = self._input_buffer[stop +len("}/"):];
                            finished = True;
                            found = True;
                            decoded_answer = rpc_result["answer"]
                            break;
            
            if found == False:
                input_not_empty = False

        rpc = {"finished": finished, "answer":decoded_answer}
        return rpc
        

    def _send_and_receive_json(self,json_request, await_answer = True):
        start = time.clock()
        self._input_buffer = ''
        self._start_tag_positions = []
        self._stop_tag_positions = []
        
        rpc_request_string = json.dumps(json_request)
        #print("rpc_request_string: "+ rpc_request_string)

        #start_stdinwrite = time.clock()
        self.rpc_json_bridge_process.stdout.flush()
        self.rpc_json_bridge_process.stdin.write('/'+rpc_request_string+'/\n')
        self.rpc_json_bridge_process.stdin.flush()
        #print("stdinwrite[ms]: "+str((time.clock() - start_stdinwrite)*1000))

        byte_count = 0
        duration_total = 0.0
        duration_total_read = 0.0
        duration_total_append = 0.0
        while await_answer:
            byte_count = byte_count +1
            
           # start_time = time.clock()
            answer_byte = self.rpc_json_bridge_process.stdout.read(1);
          #  duration_read = (time.clock() - start_time)*1000
            
            #start_time = time.clock()
            rpc_answer = self._append_answer_byte(answer_byte)
           # duration_append = (time.clock() - start_time)*1000
            
            ##duration_total = duration_total + duration_append + duration_read
            #duration_total_append = duration_total_append + duration_append
            #duration_total_read = duration_total_read + duration_read
            
  
            if rpc_answer["finished"]:
               # print("count: "+str(byte_count)+
                #      " total: "+str(duration_total)+
                #      " duration_total_append: "+str(duration_total_append)+
                #      " duration_total_append_avg: "+str(duration_total_append/byte_count)+
                #      " duration_total_read: "+str(duration_total_read)
               #       )
                #print("_send_and_receive_json[ms]: "+str((time.clock() - start)*1000))
                return rpc_answer["answer"]
            #time.sleep(0.05)
            
        
            
    def __del__(self):
        rpc_request = {
                'controll':{
                    'command':'quit',
                    'arguments':{}
                    }
            }
        self._send_and_receive_json(rpc_request, await_answer = False)

        
        
    def call(self,function_name, arguments, timeout_ms = 100):
        rpc_request = {
                'rpc':{
                    'timeout_ms':timeout_ms,
                    'request':{
                            'function':function_name,
                            'arguments':arguments
                        }
                    }
            }
        decoded_answer = self._send_and_receive_json(rpc_request)
        #print("decoded_answer: "+ str(decoded_answer)) 
        return decoded_answer['rpc']['reply']
    

    def get_server_hash(self):
        rpc_request = {
                'controll':{
                    'command':'get_hash',
                    'arguments':{}
                    }
            }
        decoded_answer = self._send_and_receive_json(rpc_request)
        #print(self._decoded_answer) 
        return decoded_answer['controll']['result']['hash']
    
    def get_version(self):
        rpc_request = {
                'controll':{
                    'command':'get_version',
                    'arguments':{}
                    }
            }
        decoded_answer = self._send_and_receive_json(rpc_request)
        
        version_info =   { "git_hash": decoded_answer['controll']['result']['git_hash'],
                   "git_unix_date":decoded_answer['controll']['result']['git_unix_date'],
                   "git_string_date":decoded_answer['controll']['result']['git_string_date']
                }
        
        return version_info
                    
    
my_env = os.environ.copy()
print("using THF_LOGGER_SERIAL "+my_env["THF_LOGGER_SERIAL"])  
print("using THF_LOGGER_BAUD "+my_env["THF_LOGGER_BAUD"])  
print("using THF_LOGGER_RPC_XML "+my_env["THF_LOGGER_RPC_XML"])  
print("using db: "+INFLUX_DB_NAME)

SIMULATE_RPC = 0
if not SIMULATE_RPC:
    proto = RPCProtocol(my_env["THF_LOGGER_SERIAL"],my_env["THF_LOGGER_BAUD"],my_env["THF_LOGGER_RPC_XML"])

    #time.sleep(0.1)
    arguments_get_adc_values = {}
    print("hash: "+proto.get_server_hash())
    print("JSON Bridge git: "+str(proto.get_version()["git_hash"]))

    result = proto.call("get_adc_values",arguments_get_adc_values)
    print("rpc_result: "+str(result))

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_IP_address = s.getsockname()[0]
    s.close()

    arguments_sys_stat = {}
    arguments_sys_stat["count_of_screens"] = 1
    arguments_sys_stat["row"] = 0
    arguments_sys_stat["screen_index"] = 0
    arguments_sys_stat["text_in"] = string_to_ord("IP: "+str(my_IP_address),20)

    result = proto.call("display_set_sysstat_screen",arguments_sys_stat)
    #time.sleep(1)
    arguments_get_adc_values = {}
    result = proto.call("get_device_descriptor",arguments_get_adc_values)
    print("rpc_result: "+str(result))


mqtt_client= mqtt.Client("client-001") 
mqtt_client.connect(BROKER)
mqtt_client.on_disconnect = mqtt_on_disconnect
mqtt_client.on_connect = mqtt_on_connect

my_env = os.environ.copy()    
client = InfluxDBClient('localhost', 8086, 'influx_user', my_env["INFLUX_USER_PASSWORD"], INFLUX_DB_NAME)
while True:
    try:
        json_body =     [{
            "measurement": "test",
            "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            "fields": {
                "test":      123            
            }
        }]
        client.write_points(json_body)
        print("influx db successfully tested.")
        break
    except InfluxDBClientError as e:
        if e.code == 404:
            print("enerlyzer db does not exist. create one.")
            client.create_database(INFLUX_DB_NAME)
        else:
            print("other error: "+str(e))

        

last_time_stamp = 0;
energy_Wh = 0.0
energy_acquisition_start = 0;
while 1:
    test_function_param = {"channel":3}
    start_time = time.clock()
    result = {}
    if SIMULATE_RPC:
        result = {}
        result["arguments"] = {}
        result["arguments"]["current_l1_avg"] = random.random()
        result["arguments"]["current_l2_avg"] = random.random()
        result["arguments"]["current_l3_avg"] = random.random()
        
        result["arguments"]["voltage_l21_avg"] = random.random()
        result["arguments"]["voltage_l32_avg"] = random.random()
        result["arguments"]["voltage_l13_avg"] = random.random()
        
        result["arguments"]["current_l1_eff"] = random.random()
        result["arguments"]["current_l2_eff"] = random.random()
        result["arguments"]["current_l3_eff"] = random.random()
        
        result["arguments"]["voltage_l21_eff"] = random.random()
        result["arguments"]["voltage_l32_eff"] = random.random()
        result["arguments"]["voltage_l13_eff"] = random.random()

        result["arguments"]["current_l1_max"] = random.random()
        result["arguments"]["current_l2_max"] = random.random()
        result["arguments"]["current_l3_max"] = random.random()
        
        result["arguments"]["voltage_l21_max"] = random.random()
        result["arguments"]["voltage_l32_max"] = random.random()
        result["arguments"]["voltage_l13_max"] = random.random()
        
        result["arguments"]["temperature_l1"] = random.random()
        result["arguments"]["temperature_l2"] = random.random()
        result["arguments"]["temperature_l3"] = random.random()
        
        result["arguments"]["voltage_aux"] = random.random()
        result["arguments"]["frequency_Hz"] = random.random()
        result["arguments"]["power"] = random.random()
        
        result["arguments"]["external_current_sensor"] = random.random()
        result["arguments"]["supply_voltage"] = random.random()
        result["arguments"]["cpu_temperature"] = random.random()
        result["arguments"]["coin_cell_mv"] = random.random()
        result["arguments"]["unix_time"] = round(time.time())
        result["arguments"]["sub_seconds"] = 0

    else:
        result = proto.call("get_power_sensor_data",{})
        
    duration = (time.clock() - start_time)*1000
    

    
    logger_unix_time = float(result["arguments"]["unix_time"])
    sub_seconds = float(result["arguments"]["sub_seconds"])
    #print("logger_unix_time: "+str(logger_unix_time))
    #print("sub_seconds: "+str(sub_seconds))
    logger_unix_time = logger_unix_time + (sub_seconds/256.0)
    interval = logger_unix_time-last_time_stamp
    if last_time_stamp == 0:
        interval = 0
        energy_acquisition_start = logger_unix_time;
        
    last_time_stamp = logger_unix_time;
    
    result["arguments"]["power"] = float(result["arguments"]["power"])/10.0*1000.0 #conversion to watt
    energy_Wh = energy_Wh + float(result["arguments"]["power"])*interval/3600.0
        
        
    storage_statvfs = os.statvfs('/media/usbstick')
    storage_avail = storage_statvfs.f_frsize * storage_statvfs.f_bavail
    storage_size = storage_statvfs.f_frsize * storage_statvfs.f_blocks
    storage_used = storage_size-storage_avail
    storage_used_percent = 100.0 * storage_used / storage_size
    

    
    json_body =     [{
        "measurement": "powerdata",
        "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        "fields": {
            "logger_time":      logger_unix_time,
            "current_l1_avg":  float(result["arguments"]["current_l1_avg"]),
            "current_l2_avg":  float(result["arguments"]["current_l2_avg"]),
            "current_l3_avg":  float(result["arguments"]["current_l3_avg"]),
            
            "voltage_l21_avg":  float(result["arguments"]["voltage_l21_avg"]),
            "voltage_l32_avg":  float(result["arguments"]["voltage_l32_avg"]),
            "voltage_l13_avg":  float(result["arguments"]["voltage_l13_avg"]),
            
            "current_l1_eff":  float(result["arguments"]["current_l1_eff"]),
            "current_l2_eff":  float(result["arguments"]["current_l2_eff"]),
            "current_l3_eff":  float(result["arguments"]["current_l3_eff"]),
            
            "voltage_l21_eff":  float(result["arguments"]["voltage_l21_eff"]),
            "voltage_l32_eff":  float(result["arguments"]["voltage_l32_eff"]),
            "voltage_l13_eff":  float(result["arguments"]["voltage_l13_eff"]),

            "current_l1_max":  float(result["arguments"]["current_l1_max"]),
            "current_l2_max":  float(result["arguments"]["current_l2_max"]),
            "current_l3_max":  float(result["arguments"]["current_l3_max"]),
            
            "voltage_l21_max":  float(result["arguments"]["voltage_l21_max"]),
            "voltage_l32_max":  float(result["arguments"]["voltage_l32_max"]),
            "voltage_l13_max":  float(result["arguments"]["voltage_l13_max"]),
            
            "temperature_l1":  float(result["arguments"]["temperature_l1"]),
            "temperature_l2":  float(result["arguments"]["temperature_l2"]),
            "temperature_l3":  float(result["arguments"]["temperature_l3"]),
            
            "voltage_aux":  float(result["arguments"]["voltage_aux"]),
            
            "frequency_Hz":  float(result["arguments"]["frequency_Hz"]),
            "power":  float(result["arguments"]["power"]),
            "external_current_sensor":  float(result["arguments"]["external_current_sensor"]),
            
            "supply_voltage":  float(result["arguments"]["supply_voltage"]),
            "cpu_temperature":  float(result["arguments"]["cpu_temperature"]),
            "coin_cell_mv":  float(result["arguments"]["coin_cell_mv"])      ,
            "energy_Wh": energy_Wh,
            "energy_start": energy_acquisition_start
            
        }
    }]
        
    protobuf_dataset = protobuf_logger_pb2.dataset()
    protobuf_dataset.logger_time =    json_body[0]["fields"]["logger_time"]
    protobuf_dataset.current_l1_avg = json_body[0]["fields"]["current_l1_avg"]
    protobuf_dataset.current_l2_avg = json_body[0]["fields"]["current_l2_avg"]
    protobuf_dataset.current_l3_avg = json_body[0]["fields"]["current_l3_avg"]
    
    protobuf_dataset.voltage_l21_avg = json_body[0]["fields"]["voltage_l21_avg"]
    protobuf_dataset.voltage_l32_avg = json_body[0]["fields"]["voltage_l32_avg"]
    protobuf_dataset.voltage_l13_avg = json_body[0]["fields"]["voltage_l13_avg"]
    
    protobuf_dataset.current_l1_eff = json_body[0]["fields"]["current_l1_eff"]
    protobuf_dataset.current_l2_eff = json_body[0]["fields"]["current_l2_eff"]
    protobuf_dataset.current_l3_eff = json_body[0]["fields"]["current_l3_eff"]

    protobuf_dataset.voltage_l21_eff = json_body[0]["fields"]["voltage_l21_eff"]
    protobuf_dataset.voltage_l32_eff = json_body[0]["fields"]["voltage_l32_eff"]
    protobuf_dataset.voltage_l13_eff = json_body[0]["fields"]["voltage_l13_eff"]
    
    protobuf_dataset.current_l1_max = json_body[0]["fields"]["current_l1_max"]
    protobuf_dataset.current_l2_max = json_body[0]["fields"]["current_l2_max"]
    protobuf_dataset.current_l3_max = json_body[0]["fields"]["current_l3_max"]
    
    protobuf_dataset.voltage_l21_max = json_body[0]["fields"]["voltage_l21_max"]
    protobuf_dataset.voltage_l32_max = json_body[0]["fields"]["voltage_l32_max"]
    protobuf_dataset.voltage_l13_max = json_body[0]["fields"]["voltage_l13_max"]

    protobuf_dataset.temperature_l1 = json_body[0]["fields"]["temperature_l1"]
    protobuf_dataset.temperature_l2 = json_body[0]["fields"]["temperature_l2"]
    protobuf_dataset.temperature_l3 = json_body[0]["fields"]["temperature_l3"]
    
    protobuf_dataset.voltage_aux = json_body[0]["fields"]["voltage_aux"]
    protobuf_dataset.frequency_Hz = json_body[0]["fields"]["frequency_Hz"]
    protobuf_dataset.power = json_body[0]["fields"]["power"]
    
    protobuf_dataset.external_current_sensor = json_body[0]["fields"]["external_current_sensor"]
    protobuf_dataset.supply_voltage = json_body[0]["fields"]["supply_voltage"]
    protobuf_dataset.cpu_temperature = json_body[0]["fields"]["cpu_temperature"]
    protobuf_dataset.coin_cell_mv = json_body[0]["fields"]["coin_cell_mv"]
    
    protobuf_dataset.used_storage_percent = storage_used_percent;
    protobuf_dataset.energy_Wh = energy_Wh;
    protobuf_dataset.energy_start = energy_acquisition_start;
    
    
   
    client.write_points(json_body)
    
    mqtt_publish_result = mqtt_client.publish("enerlyzer/live/pwr", protobuf_dataset.SerializeToString(), qos=2)
    if mqtt_publish_result.rc == mqtt.MQTT_ERR_NO_CONN:
        print("MQTT publish result: "+str(mqtt_publish_result))
        print("failed to publish MQTT. reconnect..")
        mqtt_client.reconnect();
        
    mqtt_client.loop(timeout=1.0)    
    time.sleep(0.5)

