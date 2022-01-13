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
import dbus.mainloop.glib
import dbus.exceptions

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject
from GreenPonik_BLE.bletools import BleTools
import logging

FORMAT = "%(asctime)-15s %(levelname)s %(module)s %(funcName)s \
        line-%(lineno)d: %(message)s"
logger = logging.basicConfig(
    level=logging.DEBUG, filename="/var/log/ble_server.log", format=FORMAT
)

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"
GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
GATT_DESC_IFACE = "org.bluez.GattDescriptor1"


class InvalidArgsException(dbus.exceptions.DBusException):
    """[summary]

    :param dbus: [description]
    :type dbus: [type]
    """
    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


class NotSupportedException(dbus.exceptions.DBusException):
    """[summary]

    :param dbus: [description]
    :type dbus: [type]
    """
    _dbus_error_name = "org.bluez.Error.NotSupported"


class NotPermittedException(dbus.exceptions.DBusException):
    """[summary]

    :param dbus: [description]
    :type dbus: [type]
    """
    _dbus_error_name = "org.bluez.Error.NotPermitted"


class Application(dbus.service.Object):
    """[summary]

    :param dbus: [description]
    :type dbus: [type]
    """
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.mainloop = GObject.MainLoop()
        self.bus = BleTools.get_bus()
        self.path = "/"
        self.services = []
        self.next_index = 0
        self.log = logging.getLogger('classLogger')
        dbus.service.Object.__init__(self, self.bus, self.path)

    def get_path(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        """[summary]

        :param service: [description]
        :type service: [type]
        """
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        response = {}

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response

    def register_app_callback(self):
        """[summary]
        """
        print("GATT application registered")

    def register_app_error_callback(self, error):
        """[summary]

        :param error: [description]
        :type error: [type]
        """
        print("Failed to register application: " + str(error))

    def register(self):
        """[summary]
        """
        adapter = BleTools.find_adapter(self.bus)

        service_manager = dbus.Interface(
            self.bus.get_object(BLUEZ_SERVICE_NAME, adapter), GATT_MANAGER_IFACE
        )

        service_manager.RegisterApplication(
            self.get_path(),
            {},
            reply_handler=self.register_app_callback,
            error_handler=self.register_app_error_callback,
        )

    def run(self):
        """[summary]
        """
        self.mainloop.run()

    def quit(self):
        """[summary]
        """
        print("\nGATT application terminated")
        self.mainloop.quit()


class Service(dbus.service.Object):
    """[summary]

    :param dbus: [description]
    :type dbus: [type]
    :raises InvalidArgsException: [description]
    :return: [description]
    :rtype: [type]
    """
    PATH_BASE = "/org/bluez/example/service"

    def __init__(self, index, uuid, primary):
        self.bus = BleTools.get_bus()
        self.path = self.PATH_BASE + str(index)
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        self.next_index = 0
        self.log = logging.getLogger('classLogger')
        dbus.service.Object.__init__(self, self.bus, self.path)

    def get_properties(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return {
            GATT_SERVICE_IFACE: {
                "UUID": self.uuid,
                "Primary": self.primary,
                "Characteristics": dbus.Array(
                    self.get_characteristic_paths(), signature="o"
                ),
            }
        }

    def get_path(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        """[summary]

        :param characteristic: [description]
        :type characteristic: [type]
        """
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return self.characteristics

    def get_bus(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return self.bus

    def get_next_index(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        idx = self.next_index
        self.next_index += 1

        return idx

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        """[summary]

        :param interface: [description]
        :type interface: [type]
        :raises InvalidArgsException: [description]
        :return: [description]
        :rtype: [type]
        """
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation
    [summary]

    :param dbus: [description]
    :type dbus: [type]
    """

    def __init__(self, uuid, flags, service):
        index = service.get_next_index()
        self.path = service.path + "/char" + str(index)
        self.bus = service.get_bus()
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        self.next_index = 0
        self.log = logging.getLogger('classLogger')
        dbus.service.Object.__init__(self, self.bus, self.path)

    def get_properties(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return {
            GATT_CHRC_IFACE: {
                "Service": self.service.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
                "Descriptors": dbus.Array(self.get_descriptor_paths(), signature="o"),
            }
        }

    def get_path(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        """[summary]

        :param descriptor: [description]
        :type descriptor: [type]
        """
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        """[summary]

        :param interface: [description]
        :type interface: [type]
        :raises InvalidArgsException: [description]
        :return: [description]
        :rtype: [type]
        """
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        """[summary]

        :param options: [description]
        :type options: [type]
        :raises NotSupportedException: [description]
        """
        print("Default ReadValue called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="aya{sv}")
    def WriteValue(self, value, options):
        """[summary]

        :param value: [description]
        :type value: [type]
        :param options: [description]
        :type options: [type]
        :raises NotSupportedException: [description]
        """
        print("Default WriteValue called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        """[summary]

        :raises NotSupportedException: [description]
        """
        print("Default StartNotify called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        """[summary]

        :raises NotSupportedException: [description]
        """
        print("Default StopNotify called, returning error")
        raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE, signature="sa{sv}as")
    def PropertiesChanged(self, interface, changed, invalidated):
        """[summary]

        :param interface: [description]
        :type interface: [type]
        :param changed: [description]
        :type changed: [type]
        :param invalidated: [description]
        :type invalidated: [type]
        """
        pass

    def get_bus(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        bus = self.bus

        return bus

    def get_next_index(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        idx = self.next_index
        self.next_index += 1

        return idx

    def add_timeout(self, timeout, callback):
        """[summary]

        :param timeout: [description]
        :type timeout: [type]
        :param callback: [description]
        :type callback: function
        """
        GObject.timeout_add(timeout, callback)


class Descriptor(dbus.service.Object):
    """[summary]

    :param dbus: [description]
    :type dbus: [type]
    """
    def __init__(self, uuid, flags, characteristic):
        index = characteristic.get_next_index()
        self.path = characteristic.path + "/desc" + str(index)
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        self.bus = characteristic.get_bus()
        self.log = logging.getLogger('classLogger')
        dbus.service.Object.__init__(self, self.bus, self.path)

    def get_properties(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return {
            GATT_DESC_IFACE: {
                "Characteristic": self.chrc.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
            }
        }

    def get_path(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        """[summary]

        :param interface: [description]
        :type interface: [type]
        :raises InvalidArgsException: [description]
        :return: [description]
        :rtype: [type]
        """
        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        """[summary]

        :param options: [description]
        :type options: [type]
        :raises NotSupportedException: [description]
        """
        print("Default ReadValue called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature="aya{sv}")
    def WriteValue(self, value, options):
        """[summary]

        :param value: [description]
        :type value: [type]
        :param options: [description]
        :type options: [type]
        :raises NotSupportedException: [description]
        """
        print("Default WriteValue called, returning error")
        raise NotSupportedException()


class CharacteristicUserDescriptionDescriptor(Descriptor):
    """[summary]

    :param Descriptor: [description]
    :type Descriptor: [type]
    :raises NotPermittedException: [description]
    :return: [description]
    :rtype: [type]
    """
    CUD_UUID = "2901"

    def __init__(self, bus, index, characteristic):
        self.writable = "writable-auxiliaries" in characteristic.flags
        self.value = self.array.array("B", b"This is a characteristic for testing")
        self.value = self.value.tolist()
        Descriptor.__init__(
            self, bus, index, self.CUD_UUID, ["read", "write"], characteristic
        )

    def ReadValue(self, options):
        """[summary]

        :param options: [description]
        :type options: [type]
        :return: [description]
        :rtype: [type]
        """
        return self.value

    def WriteValue(self, value, options):
        """[summary]

        :param value: [description]
        :type value: [type]
        :param options: [description]
        :type options: [type]
        :raises NotPermittedException: [description]
        """
        if not self.writable:
            raise NotPermittedException()
        self.value = value
