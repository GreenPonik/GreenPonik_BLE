import unittest
from unittest.mock import patch
import dbus
import sys
import os
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent = os.path.abspath(os.path.join(here, os.pardir))
sys.path.insert(0, parent)
from GreenPonik_BLE.gattserver import JsonService, JsonCharacteristic, GetIPCharacteristic


class TestBleServer(unittest.TestCase):
    fixtures = {
        "ssid": "ssid_init",
        "pwd": "pwd_init",
        "country": "country_init",
        "wifichange": True
    }

    @patch("GreenPonik_BLE.bletools.BleTools.get_bus")
    def test_properties(self, mock_getbus):
        i = mock_getbus()
        i.return_value = True
        jsons = JsonService(0)
        jsons.ssid = self.fixtures["ssid"]
        jsons.pwd = self.fixtures["pwd"]
        jsons.country = self.fixtures["country"]
        jsons.wifichange = self.fixtures["wifichange"]
        self.assertIsNotNone(jsons.ssid)
        self.assertIsNotNone(jsons.pwd)
        self.assertIsNotNone(jsons.country)
        self.assertIsNotNone(jsons.wifichange)
        self.assertEqual(jsons.ssid, self.fixtures["ssid"])
        self.assertEqual(jsons.pwd, self.fixtures["pwd"])
        self.assertEqual(jsons.country, self.fixtures["country"])
        self.assertEqual(jsons.wifichange, self.fixtures["wifichange"])

    @patch("GreenPonik_BLE.bletools.BleTools.get_bus")
    def test_json_charac(self, mock_getbus):
        i = mock_getbus()
        i.return_value = True
        service = JsonService(0)
        service.ssid = self.fixtures["ssid"]
        service.pwd = self.fixtures["pwd"]
        service.country = self.fixtures["country"]
        jsonc = JsonCharacteristic(service)
        result = jsonc.ReadValue()
        expected = [dbus.Byte(123), dbus.Byte(34), dbus.Byte(115), dbus.Byte(115), dbus.Byte(105), dbus.Byte(100), dbus.Byte(34), dbus.Byte(58), dbus.Byte(32), dbus.Byte(115), dbus.Byte(115), dbus.Byte(105), dbus.Byte(100), dbus.Byte(95), dbus.Byte(105), dbus.Byte(110), dbus.Byte(105), dbus.Byte(116), dbus.Byte(44), dbus.Byte(34), dbus.Byte(112), dbus.Byte(119), dbus.Byte(100), dbus.Byte(34), dbus.Byte(58), dbus.Byte(32), dbus.Byte(112), dbus.Byte(119), dbus.Byte(100), dbus.Byte(95), dbus.Byte(105), dbus.Byte(110), dbus.Byte(105), dbus.Byte(116), dbus.Byte(44), dbus.Byte(34), dbus.Byte(99), dbus.Byte(111), dbus.Byte(117), dbus.Byte(110), dbus.Byte(116), dbus.Byte(114), dbus.Byte(121), dbus.Byte(34), dbus.Byte(58), dbus.Byte(32), dbus.Byte(99), dbus.Byte(111), dbus.Byte(117), dbus.Byte(110), dbus.Byte(116), dbus.Byte(114), dbus.Byte(121), dbus.Byte(95), dbus.Byte(105), dbus.Byte(110), dbus.Byte(105), dbus.Byte(116), dbus.Byte(125)]
        self.assertEqual(result, expected)

    # @patch("GreenPonik_BLE.gattserver.JsonService")
    # @patch("GreenPonik_BLE.gattserver.GetIPCharacteristic")
    @patch("GreenPonik_BLE.bletools.BleTools.get_bus")
    def test_getip(self, mock_getbus):
        service = JsonService(0)
        i = mock_getbus()
        i.return_value = True
        service.ssid = self.fixtures["ssid"]
        service.pwd = self.fixtures["pwd"]
        service.country = self.fixtures["country"]
        getipc = GetIPCharacteristic(service)
        result = getipc.get_ip()
        print("%s" % result)
        expected = [dbus.Byte(123), dbus.Byte(34), dbus.Byte(115), dbus.Byte(115), dbus.Byte(105), dbus.Byte(100), dbus.Byte(34), dbus.Byte(58), dbus.Byte(32), dbus.Byte(34), dbus.Byte(34), dbus.Byte(44), dbus.Byte(34), dbus.Byte(105), dbus.Byte(112), dbus.Byte(97), dbus.Byte(100), dbus.Byte(114), dbus.Byte(101), dbus.Byte(115), dbus.Byte(115), dbus.Byte(101), dbus.Byte(34), dbus.Byte(58), dbus.Byte(32), dbus.Byte(34), dbus.Byte(34), dbus.Byte(44), dbus.Byte(34), dbus.Byte(110), dbus.Byte(101), dbus.Byte(119), dbus.Byte(119), dbus.Byte(105), dbus.Byte(102), dbus.Byte(105), dbus.Byte(105), dbus.Byte(115), dbus.Byte(111), dbus.Byte(107), dbus.Byte(34), dbus.Byte(58), dbus.Byte(32), dbus.Byte(34), dbus.Byte(70), dbus.Byte(97), dbus.Byte(108), dbus.Byte(115), dbus.Byte(101), dbus.Byte(34), dbus.Byte(44), dbus.Byte(34), dbus.Byte(104), dbus.Byte(110), dbus.Byte(97), dbus.Byte(109), dbus.Byte(101), dbus.Byte(34), dbus.Byte(58), dbus.Byte(32), dbus.Byte(34), dbus.Byte(76), dbus.Byte(65), dbus.Byte(80), dbus.Byte(84), dbus.Byte(79), dbus.Byte(80), dbus.Byte(45), dbus.Byte(80), dbus.Byte(65), dbus.Byte(34), dbus.Byte(125)]
        self.assertEqual(result, expected)

    # @patch("GreenPonik_BLE.gattserver.JsonService")
    # @patch("GreenPonik_BLE.gattserver.GetIPCharacteristic")
    @patch("GreenPonik_BLE.bletools.BleTools.get_bus")
    def test_set_ip_callback(self, mock_getbus):
        i = mock_getbus()
        i.return_value = True
        service = JsonService(0)
        service.ssid = self.fixtures["ssid"]
        service.pwd = self.fixtures["pwd"]
        service.country = self.fixtures["country"]
        getipc = GetIPCharacteristic(service)
        getipc.StartNotify()
        result = getipc.set_ip_callback()
        self.assertTrue(result)
        getipc.StopNotify()
        result = getipc.set_ip_callback()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
