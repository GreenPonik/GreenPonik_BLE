#!/bin/bash
# The script download dependencies and tool to start and manage the BLE server on Raspberry Pi
# Distribution Raspbian Buster
# works on:

#           -Raspberry Pi 3 A+
# Licence: GPLv3
# Author: Pierre-Antoine GROUT <pierre-antoine.grout@greenponik.com>
# Repository: https://github.com/GreenPonik/GreenPonik_BLE

DEFAULT='\033[0;39m'
WHITE='\033[0;02m'
RASPBERRY='\033[0;35m'
GREEN='\033[1;32m'
RED='\033[1;31m'

_welcome() {
    VERSION="0.0.1"
    echo -e "${RASPBERRY}\n"
    echo -e "                                                                                                                                       "
    echo -e " /888888  /8888888  /88888888 /88888888 /88   /88 /8888888   /888888  /88   /88 /888888 /88   /88       /8888888  /88       /88888888  "
    echo -e " /88__  88| 88__  88| 88_____/| 88_____/| 888 | 88| 88__  88 /88__  88| 888 | 88|_  88_/| 88  /88/      | 88__  88| 88      | 88_____/ "
    echo -e "| 88  \__/| 88  \ 88| 88      | 88      | 8888| 88| 88  \ 88| 88  \ 88| 8888| 88  | 88  | 88 /88/       | 88  \ 88| 88      | 88       "
    echo -e "| 88 /8888| 8888888/| 88888   | 88888   | 88 88 88| 8888888/| 88  | 88| 88 88 88  | 88  | 88888/        | 8888888 | 88      | 88888    "
    echo -e "| 88|_  88| 88__  88| 88__/   | 88__/   | 88  8888| 88____/ | 88  | 88| 88  8888  | 88  | 88  88        | 88__  88| 88      | 88__/    "
    echo -e "| 88  \ 88| 88  \ 88| 88      | 88      | 88\  888| 88      | 88  | 88| 88\  888  | 88  | 88\  88       | 88  \ 88| 88      | 88       "
    echo -e "|  888888/| 88  | 88| 88888888| 88888888| 88 \  88| 88      |  888888/| 88 \  88 /888888| 88 \  88      | 8888888/| 88888888| 88888888 "
    echo -e " \______/ |__/  |__/|________/|________/|__/  \__/|__/       \______/ |__/  \__/|______/|__/  \__/      |_______/ |________/|________/ "
    echo -e "                                                                                                                                       "
    echo -e "                                                    version ${VERSION}                                                                 "
    echo -e " By https://github.com/GreenPonik/GreenPonik_BLE                                                                                       "
    echo -e "${GREEN}                                                                                                                               "
    echo -e "Download dependencies and tool to start and manage the BLE server on Raspberry Pi\n\n                                                  "
}

_logger() {
    echo -e "${GREEN}"
    echo "${1}"
    echo -e "${DEFAULT}"
}


install_ble_server() {
    cd /home/greenponik
    echo "installing depedencies"

    REQUIRED_PKG="dbus"
    PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
    echo Checking for $REQUIRED_PKG: $PKG_OK
    if [ "" = "$PKG_OK" ]; then
        echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
        apt-get --yes install $REQUIRED_PKG
    else
        echo "$REQUIRED_PKG already install"
    fi
    REQUIRED_PKG="supervisor"
    PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
    echo Checking for $REQUIRED_PKG: $PKG_OK
    if [ "" = "$PKG_OK" ]; then
        echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
        apt-get --yes install $REQUIRED_PKG
    else
        echo "$REQUIRED_PKG already install"
    fi

    STATUS="$(systemctl is-active bluetooth)"
    if [ "${STATUS}" = "active" ]; then
        bluetoothctl power on && bluetoothctl pairable off && bluetoothctl discoverable off
    else 
        i=0
        while true
            (( i=i+1 ))
        do
            if (( i < 5 ))
            then
                systemctl start bluetooth
                sleep 3
                continue
            else
                bluetoothctl power on && bluetoothctl pairable off && bluetoothctl discoverable off
                break
            fi
        done
        if [ "${STATUS}" != "active" ]; then
            echo "bluetooth is not activated"
            exit 1
        fi
    fi
    wget -q --spider http://google.com
    if [ $? -eq 0 ]; then
        wget https://raw.githubusercontent.com/GreenPonik/GreenPonik_BLE/main/supervisor_ble_server.conf
        FILE=supervisor_ble_server.conf
        if [ -f "$FILE" ]; then
            if [ -s "$FILE" ]; then
                mv supervisor_ble_server.conf /etc/supervisor/conf.d/supervisor_ble_server.conf
            else
                echo "supervisor_ble_server.conf is empty"
                exit 2
            fi
        else
            echo "supervisor_ble_server.conf doesn't exist"
            exit 3
        fi
        wget https://raw.githubusercontent.com/GreenPonik/GreenPonik_BLE/main/main.template.py
        mkdir -p ble_server
        FILE=main.template.py
        if [ -f "$FILE" ]; then
            if [ -s "$FILE" ]; then
                mv main.template.py ble_server/main.py
            else
                echo "main.template.py is empty"
                exit 2
            fi
        else
            echo "main.template.py doesn't exist"
            exit 3
        fi
    else
        echo "Not connected to internet"
    fi
    REQUIRED_PKG="greenponik-ble"
    PKG_OK=$(pip3 list|grep -F $REQUIRED_PKG)
    echo Checking for $REQUIRED_PKG: $PKG_OK
    wget -q --spider http://google.com
    if [ $? -eq 0 ]; then
        if [ "" = "$PKG_OK" ]; then
            echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
            pip3 install greenponik-ble
        else
            pip3 install greenponik-ble --upgrade
        fi
    else
        echo "Not connected to internet"
    fi
    if [[ 1 -ne $(pip3 list|grep -cF "Adafruit-PlatformDetect") ]]; then
        pip3 install Adafruit-PlatformDetect
    fi
    STATUS="$(systemctl is-active supervisor)"
    if [ "${STATUS}" = "active" ]; then
        supervisorctl stop all
        supervisorctl reread
        supervisorctl update
        supervisorctl start all
    else 
        i=0
        while true
            (( i=i+1 ))
        do
            if (( i < 5 ))
            then
                systemctl start supervisor
                sleep 3
                continue
            else
                supervisorctl stop all
                supervisorctl reread
                supervisorctl update
                supervisorctl start all
                break
            fi
        done
        if [ "${STATUS}" != "active" ]; then
            echo "supervisor is not activated"
            exit 1
        fi
    fi
    echo "finish"
}

if [ $(id -u) != 0 ]; then
    echo -e "${RED}"
    echo "You need to be root to run this script! Please run 'sudo bash $0'"
    echo -e "${DEFAULT}"
    exit 1
fi

_welcome
install_ble_server
