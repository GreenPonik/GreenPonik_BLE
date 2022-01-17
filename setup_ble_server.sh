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
    /usr/bin/bluetoothctl power on && /usr/bin/bluetoothctl pairable off && /usr/bin/bluetoothctl discoverable off
    wget https://raw.githubusercontent.com/GreenPonik/GreenPonik_BLE/main/supervisor_ble_server.conf
    mv supervisor_ble_server.conf /etc/supervisor/conf.d/supervisor_ble_server.conf
    wget https://raw.githubusercontent.com/GreenPonik/GreenPonik_BLE/main/main.template.py
    mkdir -p ble_server
    mv main.template.py ble_server/main.py
    REQUIRED_PKG="greenponik-ble"
    PKG_OK=$(pip3 list|grep -F $REQUIRED_PKG)
    echo Checking for $REQUIRED_PKG: $PKG_OK
    if [ "" = "$PKG_OK" ]; then
        echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
        pip3 install greenponik-ble
    else
        pip3 install greenponik-ble --upgrade
    fi
    if [[ 1 -ne $(pip3 list|grep -cF "Adafruit-PlatformDetect") ]]; then
        pip3 install Adafruit-PlatformDetect
    fi
    supervisorctl stop all
    supervisorctl reread
    supervisorctl update
    supervisorctl start all

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
