#!/bin/sh

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"


apt update
apt-get -y install curl htop apt-transport-https




#install influxdb
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
curl https://packagecloud.io/gpg.key | sudo apt-key add -

echo "deb https://repos.influxdata.com/debian stretch stable" | tee /etc/apt/sources.list.d/influxdb.list
echo "deb https://packagecloud.io/grafana/stable/debian/ stretch main" | tee /etc/apt/sources.list.d/grafana.list

#install python

apt update
apt-get -y install influxdb python-pip python-influxdb python-protobuf grafana
cp -rf $SCRIPTPATH/../etc/influxdb/influxdb.conf /etc/influxdb/influxdb.conf
cp -rf $SCRIPTPATH/../etc/grafana/grafana.ini /etc/grafana/grafana.ini

pip install paho-mqtt

mkdir /home/enerlyzer_receiver/influx_data
chown /home/enerlyzer_receiver/influx_data


systemctl daemon-reload
systemctl start grafana-server
service influxdb start
systemctl enable grafana-server.service
systemctl enable influxdb
