#!/bin/bash
TARGET=/etc/systemd/system/
#TARGET=~/test/

if [ ! -d "$TARGET" ]; then
    # Control will enter here if $DIRECTORY doesn't exist.
    mkdir $TARGET
fi



for filename_path in ../etc/systemd/system/*.sh; do
    #echo $filename | sed 's:.*/::'
    file_name=$(echo $filename_path | sed 's:.*/::')
    
    
    if [ -d "$TARGET$file_name" ]; then
    # Control will enter here if $DIRECTORY exists.
        sudo systemctl stop $file_name
        sudo rm $TARGET$file_name
    fi
    
    sudo cp $filename_path $TARGET$file_name
    
    sudo systemctl start $file_name
    sudo systemctl enable $file_name
done
