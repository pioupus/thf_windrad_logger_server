#!/bin/bash

USER_NAME=enerlyzer_receiver

apt-get update
apt-get install pwgen
#useradd -m $USER_NAME
adduser $USER_NAME sudo
chsh -s /bin/bash $USER_NAME

read -s -p "Enter a new password for $USER_NAME: " PASS1
echo ""
read -s -p "Repeat password for $USER_NAME: " PASS2

if [ "$PASS1" = "$PASS2" ]; then
    echo -e "$PASS1\n$PASS1" | passwd $USER_NAME
    echo MY_PASSWORD=$PASS1 >> /home/$USER_NAME/enerlyzer_receiver.env
    echo INFLUX_USER_PASSWORD=`pwgen -N 1` >> /home/$USER_NAME/enerlyzer_receiver.env
    echo INFLUX_READER_PASSWORD=`pwgen -N 1` >> /home/$USER_NAME/enerlyzer_receiver.env

    echo "set -a; source /home/enerlyzer_receiver/enerlyzer_receiver.env; set +a" >> /home/$USER_NAME/.bashrc
    chown $USER_NAME /home/$USER_NAME/enerlyzer_receiver.env
fi

sudo -u enerlyzer_receiver bash << EOF
cd /home/enerlyzer_receiver/thf_windrad_logger_server/update/
./do_update.py
./run_run_once_files.py
./install_services.sh
EOF

systemctl restart influxdb
systemctl restart receive_logger
