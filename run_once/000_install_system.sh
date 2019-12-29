#!/bin/sh

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"


echo sudo | sudo -S apt-get update
echo $MY_PASSWORD | sudo -S apt-get -y install curl htop apt-transport-https software-properties-common
echo $MY_PASSWORD | sudo -S add-apt-repository ppa:certbot/certbot
echo $MY_PASSWORD | sudo -S apt-get update
echo $MY_PASSWORD | sudo -S apt-get -y install python-certbot-nginx


#install influxdb
echo $MY_PASSWORD | sudo -S curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo $MY_PASSWORD |sudo -S wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
#echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"


echo $MY_PASSWORD | sudo -S apt update
#install mosquitto
echo $MY_PASSWORD | sudo apt-get install mosquitto mosquitto-clients
echo $MY_PASSWORD | sudo mosquitto_passwd -c /etc/mosquitto/passwd enerlyzer_thf
echo $MY_PASSWORD | sudo mosquitto_passwd /etc/mosquitto/passwd mqtt_local_user
echo $MY_PASSWORD | sudo mosquitto_passwd /etc/mosquitto/passwd enerlyzer_desk


echo $MY_PASSWORD | sudo echo allow_anonymous false > /etc/mosquitto/conf.d/default.conf
echo $MY_PASSWORD | sudo echo password_file /etc/mosquitto/passwd >> /etc/mosquitto/conf.d/default.conf




#install python

echo $MY_PASSWORD | sudo -S apt-get -y install influxdb python-pip python-influxdb python-protobuf grafana
echo $MY_PASSWORD | sudo -S cp -rf $SCRIPTPATH/../etc/influxdb/influxdb.conf /etc/influxdb/influxdb.conf
echo $MY_PASSWORD | sudo -S cp -rf $SCRIPTPATH/../etc/grafana/grafana.ini /etc/grafana/grafana.ini

echo $MY_PASSWORD | sudo -S pip install paho-mqtt

mkdir /home/enerlyzer_receiver/influx_data
echo $MY_PASSWORD | sudo -S chown influxdb /home/enerlyzer_receiver/influx_data


echo $MY_PASSWORD | sudo -S systemctl daemon-reload
echo $MY_PASSWORD | sudo -S systemctl start grafana-server
echo $MY_PASSWORD | sudo -S service influxdb start
echo $MY_PASSWORD | sudo -S systemctl enable grafana-server.service
echo $MY_PASSWORD | sudo -S systemctl enable influxdb
