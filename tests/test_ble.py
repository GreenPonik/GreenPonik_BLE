import dbus
import sys
import os

here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent = os.path.abspath(os.path.join(here, os.pardir))
sys.path.insert(0, parent)

from GreenPonik_BLE.gattserver import (
    JsonService,
    JsonCharacteristic,
    GetIPCharacteristic,
)

# from GreenPonik_BLE.gattserver.GetIPCharacteristic import _get_ifconfig, _get_iwconfig

import unittest
from unittest.mock import patch, MagicMock


class TestBleServer(unittest.TestCase):
    fixtures = {
        "ssid": "ssid_init",
        "pwd": "pwd_init",
        "country": "country_init",
        "wifichange": True,
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
        # TODO use decoded dbusByte result instead of using expected dbus.byte array
        # for now it isn't human unreadable
        expected = [
            dbus.Byte(123),
            dbus.Byte(34),
            dbus.Byte(115),
            dbus.Byte(115),
            dbus.Byte(105),
            dbus.Byte(100),
            dbus.Byte(34),
            dbus.Byte(58),
            dbus.Byte(32),
            dbus.Byte(115),
            dbus.Byte(115),
            dbus.Byte(105),
            dbus.Byte(100),
            dbus.Byte(95),
            dbus.Byte(105),
            dbus.Byte(110),
            dbus.Byte(105),
            dbus.Byte(116),
            dbus.Byte(44),
            dbus.Byte(34),
            dbus.Byte(112),
            dbus.Byte(119),
            dbus.Byte(100),
            dbus.Byte(34),
            dbus.Byte(58),
            dbus.Byte(32),
            dbus.Byte(112),
            dbus.Byte(119),
            dbus.Byte(100),
            dbus.Byte(95),
            dbus.Byte(105),
            dbus.Byte(110),
            dbus.Byte(105),
            dbus.Byte(116),
            dbus.Byte(44),
            dbus.Byte(34),
            dbus.Byte(99),
            dbus.Byte(111),
            dbus.Byte(117),
            dbus.Byte(110),
            dbus.Byte(116),
            dbus.Byte(114),
            dbus.Byte(121),
            dbus.Byte(34),
            dbus.Byte(58),
            dbus.Byte(32),
            dbus.Byte(99),
            dbus.Byte(111),
            dbus.Byte(117),
            dbus.Byte(110),
            dbus.Byte(116),
            dbus.Byte(114),
            dbus.Byte(121),
            dbus.Byte(95),
            dbus.Byte(105),
            dbus.Byte(110),
            dbus.Byte(105),
            dbus.Byte(116),
            dbus.Byte(125),
        ]
        self.assertEqual(result, expected)

    @patch("GreenPonik_BLE.bletools.BleTools.get_bus")
    @patch.object(GetIPCharacteristic, "_get_ifconfig")
    @patch.object(GetIPCharacteristic, "_get_iwconfig")
    def test_getip(self, mock_iwconfig, mock_ifconfig, mock_getbus):
        i = mock_getbus()
        i.return_value = True

        service = JsonService(0)
        service.ssid = self.fixtures["ssid"]
        service.pwd = self.fixtures["pwd"]
        service.country = self.fixtures["country"]
        ip_address = ["192.168.0.1", "", None]
        ssid = [service.ssid, ""]
        newwifiisok = None

        for ip in ip_address:
            for myssid in ssid:
                if ip == "192.168.0.1" and myssid == service.ssid:
                    newwifiisok = True
                else:
                    newwifiisok = False
                expected_data = (
                    '{"ssid": "%s","ipadresse": "%s","newwifiisok": "%s","hname": "%s"}'
                    % (
                        myssid,
                        ip if None is not ip else "",
                        newwifiisok,
                        os.uname().nodename,
                    )
                )

                mock_ifconfig.return_value = ip
                mock_iwconfig.return_value = myssid

                result = None
                getipc = GetIPCharacteristic(service)
                result = getipc.get_ip()

                decoded_result_from_dbus_byte = []
                for r in result:
                    decoded_result_from_dbus_byte.append(" ".join(str(r)))
                decoded_result = "".join(s for s in decoded_result_from_dbus_byte)

                self.assertIsNotNone(decoded_result)
                self.assertEqual(decoded_result, expected_data)

    @patch("GreenPonik_BLE.bletools.BleTools.get_bus")
    @patch.object(GetIPCharacteristic, "_get_ifconfig")
    @patch.object(GetIPCharacteristic, "_get_iwconfig")
    def test_set_ip_callback(self, mock_iwconfig, mock_ifconfig, mock_getbus):
        i = mock_getbus()
        i.return_value = True

        service = JsonService(0)
        service.ssid = self.fixtures["ssid"]
        service.pwd = self.fixtures["pwd"]
        service.country = self.fixtures["country"]
        ip_address = "192.168.0.1"

        mock_ifconfig.return_value = ip_address
        mock_iwconfig.return_value = service.ssid

        result = None
        getipc = GetIPCharacteristic(service)
        getipc.StartNotify()
        result = getipc.set_ip_callback()
        self.assertIsNotNone(result)
        self.assertTrue(result)
        getipc.StopNotify()
        result = getipc.set_ip_callback()
        self.assertIsNotNone(result)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
