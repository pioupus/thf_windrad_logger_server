#!/bin/sh

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"


echo $MY_PASSWORD | sudo -S apt-get update
echo $MY_PASSWORD | sudo -S apt-get -y install curl htop apt-transport-https




#install influxdb
echo $MY_PASSWORD | sudo -S curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo $MY_PASSWORD | sudo -S curl https://packagecloud.io/gpg.key | sudo apt-key add -

echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
echo "deb https://packagecloud.io/grafana/stable/debian/ stretch main" | sudo tee /etc/apt/sources.list.d/grafana.list

#install python

echo $MY_PASSWORD | sudo -S apt update
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
