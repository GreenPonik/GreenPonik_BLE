#!/usr/bin/python3

"""Copyright (c) 2019, Douglas Otwell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import dbus
import json
import subprocess
import os
import logging

from GreenPonik_BLE.advertisement import Advertisement
from GreenPonik_BLE.service import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000


class BleApplication(Application):
    pass


class JsonAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        hname = os.uname()
        self.add_local_name(hname[1])
        self.include_tx_power = True


class JsonService(Service):
    JSON_SVC_UUID = "00000001-9e3e-4800-9fa6-fd34f6571ad7"
    logging.basicConfig(level=logging.DEBUG, filename="/var/log/ble_server.log")

    def __init__(self, index):
        self.ssid = "ssid_init"
        self.pwd = "pwd_init"
        self.country = "country_init"
        self.wifichange = False

        Service.__init__(self, index, self.JSON_SVC_UUID, True)
        self.add_characteristic(JsonCharacteristic(self))
        self.add_characteristic(GetIPCharacteristic(self))

    def set_ssid(self, ssid):
        self.ssid = ssid

    def get_ssid(self):
        return self.ssid

    def set_pwd(self, pwd):
        self.pwd = pwd

    def get_pwd(self):
        return self.pwd

    def set_country(self, country):
        self.country = country

    def get_country(self):
        return self.country

    def set_wifichange(self, wifichange):
        self.wifichange = wifichange

    def get_wifichange(self):
        return self.wifichange

    def sta_configurator(self, ssid, passphrase, country_code):
        """
        @brief
        wifi sta configurator
        """
        print("Hello sta_configurator")
        try:
            """
            cmd need sudo becacd APuse the command is send through ssh to localhost from docker container
            in standalone mode the command need sudo
            """
            cmd = [
                "sudo",
                "bash",
                # "%s/ap_sta_config.sh" % AP_STA_DIR,
                "/var/lib/waterbrain/AP_STA_RPI_SAME_WIFI_CHIP/ap_sta_config.sh",
                "--client",
                ssid,
                passphrase,
                "--country",
                country_code,
                "--sta-only",
            ]
            print("first try")
            try:
                ret = subprocess.check_output(" ".join(cmd), shell=True).decode("utf-8")
                logging.debug("return of subprocess {}".format(ret))
                r = {
                    "ssid": ssid,
                    "passphrase": passphrase,
                    "country_code": country_code,
                }
                print("second try")
            except Exception as e:
                print("first except")
                logging.error("error subprocess {}".format(e))
                r = None
                pass
            logging.debug("sta_configurator returns: {}".format(r))
            return r
        except Exception as e:
            print("second except")
            logging.error("sta configurator failed {}".format(e))


class JsonCharacteristic(Characteristic):
    JSON_CHARACTERISTIC_UUID = "00000002-9e3e-4800-9fa6-fd34f6571ad7"

    def __init__(self, service):
        Characteristic.__init__(
            self, self.JSON_CHARACTERISTIC_UUID, ["read", "write-without-response"], service
        )
        self.add_descriptor(JSONDescriptor(self))

    def WriteValue(self, value, options=None):
        val = "".join(chr(i) for i in value)
        jsonval = json.loads(val)
        self.service.set_ssid(jsonval["ssid"])
        self.service.set_pwd(jsonval["pwd"])
        self.service.set_country(jsonval["country"])
        self.service.set_wifichange(False)

        print("Ready to change the wifi configuration")
        logging.debug("ssid : %s , pass : %s , country : %s", self.service.get_ssid(), self.service.get_pwd(), self.service.get_country())
        self.service.sta_configurator(
            self.service.get_ssid(), self.service.get_pwd(), self.service.get_country()
        )

    def ReadValue(self, options=None):
        value = []

        ssid = self.service.get_ssid()
        pwd = self.service.get_pwd()
        country = self.service.get_country()
        data = '{"ssid": %s,"pwd": %s,"country": %s}' % (ssid, pwd, country)

        for c in data:
            value.append(dbus.Byte(c.encode()))

        print(value)
        return value


class GetIPCharacteristic(Characteristic):
    GETIP_CHARACTERISTIC_UUID = "00000003-9e3e-4800-9fa6-fd34f6571ad7"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.GETIP_CHARACTERISTIC_UUID, ["notify", "read"], service
        )
        self.add_descriptor(GetIPDescriptor(self))

    def get_ip(self):
        value = []
        ipaddress = os.popen(
            "ifconfig wlan0 \
            | grep '\<inet\>' \
            | awk -F \" \" '{print $2}'"
        ).read()
        ssid = (
            os.popen(
                "iwconfig wlan0 \
                        | grep 'ESSID' \
                        | awk '{print $4}' \
                        | awk -F\\\" '{print $2}'"
            )
            .read()
            .rstrip("\n")
        )

        ssidsend = self.service.get_ssid()
        logging.debug("ssidsend : %s ssidRPI : %s", ssidsend, ssid)
        if (ssid == ssidsend) and ipaddress != "":
            self.service.set_wifichange(True)
        else:
            self.service.set_wifichange(False)

        newwifiisok = self.service.get_wifichange()
        hname = os.uname()
        data = '{"ssid": "%s","ipadresse": "%s","newwifiisok": "%s","hname": "%s"}' % (
            ssid.strip(),
            ipaddress.strip(),
            newwifiisok,
            hname[1],
        )

        for c in data:
            value.append(dbus.Byte(c.encode()))

        return value

    def set_ip_callback(self):
        if self.notifying:
            value = self.get_ip()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        value = self.get_ip()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_ip_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options=None):
        value = self.get_ip()

        return value


class JSONDescriptor(Descriptor):
    JSON_DESCRIPTOR_UUID = "2901"
    JSON_DESCRIPTOR_VALUE = "Send and Receive JSON data"

    def __init__(self, characteristic):
        Descriptor.__init__(self, self.JSON_DESCRIPTOR_UUID, ["read"], characteristic)

    def ReadValue(self, options=None):
        value = []
        desc = self.JSON_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


class GetIPDescriptor(Descriptor):
    GETIP_DESCRIPTOR_UUID = "2901"
    GETIP_DESCRIPTOR_VALUE = "Receive IP of RPI"

    def __init__(self, characteristic):
        Descriptor.__init__(self, self.GETIP_DESCRIPTOR_UUID, ["read"], characteristic)

    def ReadValue(self, options=None):
        value = []
        desc = self.GETIP_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value
