#!/bin/bash

USER_NAME=enerlyzer_receiver

apt-get update
apt-get install pwgen
#useradd -m $USER_NAME
adduser $USER_NAME sudo
 
read -s -p "Enter a new password for $USER_NAME: " PASS1
echo ""
read -s -p "Repeat password for $USER_NAME: " PASS2

if [ "$PASS1" = "$PASS2" ]; then
    echo -e "$PASS1\n$PASS1" | passwd $USER_NAME
    echo MY_PASSWORD=$PASS1 >> /home/$USER_NAME/enerlyzer_receiver.env
    echo INFLUX_USER_PASSWORD=`pwgen -N 1` >> /home/$USER_NAME/enerlyzer_receiver.env

    echo "set -a; source /home/enerlyzer_receiver/enerlyzer_receiver.env; set +a" >> /home/$USER_NAME/.bashrc
fi

sudo -u enerlyzer_receiver bash << EOF
~/thf_windrad_logger_server/update/./do_update.py
EOF
