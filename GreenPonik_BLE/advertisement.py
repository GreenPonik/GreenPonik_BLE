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
import dbus.service

from GreenPonik_BLE.bletools import BleTools
from GreenPonik_BLE.service import InvalidArgsException
from GreenPonik_BLE.service import logger
import logging

BLUEZ_SERVICE_NAME = "org.bluez"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"


class Advertisement(dbus.service.Object):
    """[summary]

    :param dbus: [description]
    :type dbus: [type]
    :raises InvalidArgsException: [description]
    :return: [description]
    :rtype: [type]
    """
    PATH_BASE = "/org/bluez/example/advertisement"

    def __init__(self, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = BleTools.get_bus()
        self.ad_type = advertising_type
        self.local_name = None
        self.service_uuids = None
        self.solicit_uuids = None
        self.manufacturer_data = None
        self.service_data = None
        self.include_tx_power = None
        self.log = logging.getLogger('classLogger')
        dbus.service.Object.__init__(self, self.bus, self.path)

    def get_properties(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        properties = dict()
        properties["Type"] = self.ad_type

        if self.local_name is not None:
            properties["LocalName"] = dbus.String(self.local_name)

        if self.service_uuids is not None:
            properties["ServiceUUIDs"] = dbus.Array(self.service_uuids, signature="s")
        if self.solicit_uuids is not None:
            properties["SolicitUUIDs"] = dbus.Array(self.solicit_uuids, signature="s")
        if self.manufacturer_data is not None:
            properties["ManufacturerData"] = dbus.Dictionary(
                self.manufacturer_data, signature="qv"
            )

        if self.service_data is not None:
            properties["ServiceData"] = dbus.Dictionary(
                self.service_data, signature="sv"
            )
        if self.include_tx_power is not None:
            properties["IncludeTxPower"] = dbus.Boolean(self.include_tx_power)

        if self.local_name is not None:
            properties["LocalName"] = dbus.String(self.local_name)

        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return dbus.ObjectPath(self.path)

    def add_local_name(self, name):
        """[summary]

        :param name: [description]
        :type name: [type]
        """
        if not self.local_name:
            self.local_name = ""
        self.local_name = dbus.String(name)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        """[summary]

        :param interface: [description]
        :type interface: [type]
        :raises InvalidArgsException: [description]
        :return: [description]
        :rtype: [type]
        """
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature="", out_signature="")
    def Release(self):
        """[summary]
        """
        print("%s: Released!" % self.path)

    def register_ad_callback(self):
        """[summary]
        """
        print("GATT advertisement registered")

    def register_ad_error_callback(self):
        """[summary]
        """
        print("Failed to register GATT advertisement")

    def register(self):
        """[summary]
        """
        bus = BleTools.get_bus()
        adapter = BleTools.find_adapter(bus)

        ad_manager = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter), LE_ADVERTISING_MANAGER_IFACE
        )
        ad_manager.RegisterAdvertisement(
            self.get_path(),
            {},
            reply_handler=self.register_ad_callback,
            error_handler=self.register_ad_error_callback,
        )
