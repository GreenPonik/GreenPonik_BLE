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

from GreenPonik_BLE.advertisement import Advertisement
from GreenPonik_BLE.service import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000


import platform
from adafruit_platformdetect import Detector
detector = Detector()
is_rpi3aplus = "armv7l" == platform.machine() and detector.board.RASPBERRY_PI_3A_PLUS


class BleApplication(Application):
    """[summary]

    :param Application: [description]
    :type Application: [type]
    """

    pass


class JsonAdvertisement(Advertisement):
    """[summary]

    :param Advertisement: [description]
    :type Advertisement: [type]
    """

    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        hname = os.uname()
        self.add_local_name(hname[1])
        self.include_tx_power = True


class JsonService(Service):
    """[summary]

    :param Service: [description]
    :type Service: [type]
    :return: [description]
    :rtype: [type]
    """

    JSON_SVC_UUID = "00000001-9e3e-4800-9fa6-fd34f6571ad7"

    def __init__(self, index):
        f = open("/etc/wpa_supplicant/wpa_supplicant.conf", "r")
        for x in f:
            if "ssid=\"" in x:
                self.ssid = x.split('"')[-2]
            elif "psk" in x:
                self.pwd = x.split('"')[-2]
            elif "country" in x:
                self.country = x.split('=')[-1].strip('\n')
        self.wifichange = False
        Service.__init__(self, index, self.JSON_SVC_UUID, True)
        self.add_characteristic(JsonCharacteristic(self))
        self.add_characteristic(GetIPCharacteristic(self))

    def set_ssid(self, ssid):
        """[summary]

        :param ssid: [description]
        :type ssid: [type]
        """
        self.ssid = ssid

    def get_ssid(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return self.ssid

    def set_pwd(self, pwd):
        """[summary]

        :param pwd: [description]
        :type pwd: [type]
        """
        self.pwd = pwd

    def get_pwd(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return self.pwd

    def set_country(self, country):
        """[summary]

        :param country: [description]
        :type country: [type]
        """
        self.country = country

    def get_country(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return self.country

    def set_wifichange(self, wifichange):
        """[summary]

        :param wifichange: [description]
        :type wifichange: [type]
        """

        self.wifichange = wifichange

    def get_wifichange(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return self.wifichange

    def sta_configurator(self, ssid, passphrase, country_code):
        """[summary]

        :param ssid: [description]
        :type ssid: [type]

        :param passphrase: [description]
        :type passphrase: [type]

        :param country_code: [description]
        :type country_code: [type]

        :return: [description]
        :rtype: [type]
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
                self.log.debug("return of subprocess {}".format(ret))
                r = {
                    "ssid": ssid,
                    "passphrase": passphrase,
                    "country_code": country_code,
                }
                print("second try")
            except Exception as e:
                print("first except")
                self.log.error("error subprocess {}".format(e))
                r = None
                pass
            self.log.debug("sta_configurator returns: {}".format(r))
            return r
        except Exception as e:
            print("second except")
            self.log.error("sta configurator failed {}".format(e))


class JsonCharacteristic(Characteristic):
    JSON_CHARACTERISTIC_UUID = "00000002-9e3e-4800-9fa6-fd34f6571ad7"

    def __init__(self, service):
        Characteristic.__init__(
            self,
            self.JSON_CHARACTERISTIC_UUID,
            ["read", "write-without-response"],
            service,
        )
        self.add_descriptor(JSONDescriptor(self))

    def WriteValue(self, value, options=None):
        """[summary]

        :param value: [description]
        :type value: [type]
        :param options: [description], defaults to None
        :type options: [type], optional
        """
        val = "".join(chr(i) for i in value)
        jsonval = json.loads(val)
        self.service.set_ssid(jsonval["ssid"])
        self.service.set_pwd(jsonval["pwd"])
        self.service.set_country(jsonval["country"])
        self.service.set_wifichange(False)

        print("Ready to change the wifi configuration")
        self.log.debug(
            "ssid : %s , pass : %s , country : %s",
            self.service.get_ssid(),
            self.service.get_pwd(),
            self.service.get_country(),
        )
        self.service.sta_configurator(
            self.service.get_ssid(), self.service.get_pwd(), self.service.get_country()
        )

    def ReadValue(self, options=None):
        """[summary]

        :param options: [description], defaults to None
        :type options: [type], optional
        :return: [description]
        :rtype: [type]
        """
        value = []

        ssid = self.service.get_ssid()
        pwd = self.service.get_pwd()
        country = self.service.get_country()
        data = '{"ssid": %s,"pwd": %s,"country": %s}' % (ssid, pwd, country)

        for c in data:
            value.append(dbus.Byte(c.encode()))

        return value


class GetIPCharacteristic(Characteristic):
    """[summary]

    :param Characteristic: [description]
    :type Characteristic: [type]
    :return: [description]
    :rtype: [type]
    """

    GETIP_CHARACTERISTIC_UUID = "00000003-9e3e-4800-9fa6-fd34f6571ad7"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.GETIP_CHARACTERISTIC_UUID, ["notify", "read"], service
        )
        self.add_descriptor(GetIPDescriptor(self))

    def _get_ifconfig(self):
        ret = None
        try:
            if is_rpi3aplus:
                cmd = [
                    "ifconfig",
                    "wlan0",
                    "| grep -w 'inet' || echo 'None';",
                ]
                raw_output = subprocess.check_output(" ".join(cmd), shell=True).decode("utf-8")
                ret = raw_output.split()[1]

        except Exception as e:
            self.log.error("{}".format(e))
        return ret

    def _get_iwconfig(self):
        ret = None
        try:
            if is_rpi3aplus:
                cmd = [
                    "iwconfig",
                    "wlan0",
                    "|",
                    "grep",
                    "ESSID:",
                ]
                raw_output = subprocess.check_output(" ".join(cmd), shell=True).decode("utf-8")
                ret = raw_output.split(":")[1].replace('"', "").replace("/", "").strip()
        except Exception as e:
            self.log.error("{}".format(e))
        return ret

    def get_ip(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        value = []
        ipaddress = self._get_ifconfig()
        ssid = self._get_iwconfig()
        ssidsend = self.service.get_ssid()

        self.log.debug("ssidsend : %s ssidRPI : %s", ssidsend, ssid)
        if (ssid == ssidsend) and ipaddress != "" and ipaddress is not None:
            self.service.set_wifichange(True)
        else:
            self.service.set_wifichange(False)

        newwifiisok = self.service.get_wifichange()
        hname = os.uname()
        data = '{"ssid": "%s","ipadresse": "%s","newwifiisok": "%s","hname": "%s"}' % (
            ssid.strip(),
            ipaddress.strip() if None is not ipaddress else "",
            newwifiisok,
            hname[1],
        )

        for c in data:
            value.append(dbus.Byte(c.encode()))

        return value

    def set_ip_callback(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        if self.notifying:
            value = self.get_ip()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        """[summary]"""
        if self.notifying:
            return

        self.notifying = True
        value = self.get_ip()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_ip_callback)

    def StopNotify(self):
        """[summary]"""
        self.notifying = False

    def ReadValue(self, options=None):
        """[summary]

        :param options: [description], defaults to None
        :type options: [type], optional
        :return: [description]
        :rtype: [type]
        """
        value = self.get_ip()

        return value


class JSONDescriptor(Descriptor):
    """[summary]

    :param Descriptor: [description]
    :type Descriptor: [type]
    :return: [description]
    :rtype: [type]
    """

    JSON_DESCRIPTOR_UUID = "2901"
    JSON_DESCRIPTOR_VALUE = "Send and Receive JSON data"

    def __init__(self, characteristic):
        Descriptor.__init__(self, self.JSON_DESCRIPTOR_UUID, ["read"], characteristic)

    def ReadValue(self, options=None):
        """[summary]

        :param options: [description], defaults to None
        :type options: [type], optional
        :return: [description]
        :rtype: [type]
        """
        value = []
        desc = self.JSON_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


class GetIPDescriptor(Descriptor):
    """[summary]

    :param Descriptor: [description]
    :type Descriptor: [type]
    :return: [description]
    :rtype: [type]
    """

    GETIP_DESCRIPTOR_UUID = "2901"
    GETIP_DESCRIPTOR_VALUE = "Receive IP of RPI"

    def __init__(self, characteristic):
        Descriptor.__init__(self, self.GETIP_DESCRIPTOR_UUID, ["read"], characteristic)

    def ReadValue(self, options=None):
        """[summary]

        :param options: [description], defaults to None
        :type options: [type], optional
        :return: [description]
        :rtype: [type]
        """
        value = []
        desc = self.GETIP_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value
