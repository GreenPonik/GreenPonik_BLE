[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=GreenPonik_GreenPonik_BLE&metric=alert_status)](https://sonarcloud.io/dashboard?id=GreenPonik_GreenPonik_BLE)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=GreenPonik_GreenPonik_BLE&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=GreenPonik_GreenPonik_BLE)

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=GreenPonik_GreenPonik_BLE&metric=ncloc)](https://sonarcloud.io/dashboard?id=GreenPonik_GreenPonik_BLE)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=GreenPonik_GreenPonik_BLE&metric=duplicated_lines_density)](https://sonarcloud.io/dashboard?id=GreenPonik_GreenPonik_BLE)

[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=GreenPonik_GreenPonik_BLE&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=GreenPonik_GreenPonik_BLE)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=GreenPonik_GreenPonik_BLE&metric=security_rating)](https://sonarcloud.io/dashboard?id=GreenPonik_GreenPonik_BLE)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=GreenPonik_GreenPonik_BLE&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=GreenPonik_GreenPonik_BLE)

![Upload Python Package](https://github.com/GreenPonik/GreenPonik_BLE/workflows/Upload%20Python%20Package/badge.svg?event=release)

# GreenPonik_BLE

## A python3 project to use Bluetooth BLE on raspberry pi

## ! Only tested on Raspberry Pi 3 A+

# Table of Contents

- [Installation](#installation)
- [Examples](#example)
- [Credits](#credits)

## Installation

### Dependencies

```shell
sudo apt-get install dbus supervisor
```

### Development / Tests needs

```shell
sudo apt-get update && sudo apt-get install -y \
python3-gi-cairo \
python3-dbus \
python3-gi \
python3-gi-cairo \
python-gobject \
libdbus-1-dev libdbus-glib-1-dev

python3 -m venv venv
```

on linux

```shell
source venv/bin/activate
```

or on windows

```shell
venv/Scripts/activate
```

on CI linux runner

```shell
pip3 install dbus-python pycairo PyGObject
```

```shell

pip install -r requirements.txt
```

### Script to install

```shell
sudo bash setup_ble_server.sh
```

## Example

[here the example of how to implement the BLE server](example/main.py)

## Credits

Write by Pierre Antoine Grout, from [GreenPonik](https://www.greenponik.com), 2021 <br>
Inspired by [https://github.com/Douglas6/cputemp](https://github.com/Douglas6/cputemp) thank you [https://github.com/Douglas6](https://github.com/Douglas6)
