import unittest
from unittest.mock import patch, MagicMock
import subprocess
from agentic_adb.device_utils import _get_android_devices, _get_ios_devices, resolve_device
from agentic_adb.exceptions import DeviceNotFoundError

class TestDeviceUtils(unittest.TestCase):

    @patch('agentic_adb.device_utils.subprocess.run')
    def test_get_android_devices_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "List of devices attached\nemulator-5554\tdevice\ndevice_2\toffline\n"
        mock_run.return_value = mock_result

        devices = _get_android_devices()
        self.assertEqual(devices, ["emulator-5554"])

    @patch('agentic_adb.device_utils.subprocess.run')
    def test_get_ios_devices_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "iPhone 14 | 1111-2222 | Booted | simulator | iOS 16.4\nSome other line\n"
        mock_run.return_value = mock_result

        devices = _get_ios_devices()
        self.assertEqual(devices, ["1111-2222"])

    @patch('agentic_adb.device_utils._get_android_devices')
    @patch('agentic_adb.device_utils._get_ios_devices')
    def test_resolve_device_no_device_id_single_android(self, mock_ios, mock_android):
        mock_android.return_value = ["emulator-5554"]
        mock_ios.return_value = []

        device_id, os_type = resolve_device()
        self.assertEqual(device_id, "emulator-5554")
        self.assertEqual(os_type, "android")

    @patch('agentic_adb.device_utils._get_android_devices')
    @patch('agentic_adb.device_utils._get_ios_devices')
    def test_resolve_device_no_device_id_multiple_fails(self, mock_ios, mock_android):
        mock_android.return_value = ["emulator-5554"]
        mock_ios.return_value = ["1111-2222"]

        with self.assertRaises(DeviceNotFoundError):
            resolve_device()

    @patch('agentic_adb.device_utils._get_android_devices')
    @patch('agentic_adb.device_utils._get_ios_devices')
    def test_resolve_device_with_device_id(self, mock_ios, mock_android):
        mock_android.return_value = ["emulator-5554"]
        mock_ios.return_value = ["1111-2222"]

        device_id, os_type = resolve_device(device_id="1111-2222")
        self.assertEqual(device_id, "1111-2222")
        self.assertEqual(os_type, "ios")

    @patch('agentic_adb.device_utils._get_android_devices')
    @patch('agentic_adb.device_utils._get_ios_devices')
    def test_resolve_device_not_found(self, mock_ios, mock_android):
        mock_android.return_value = ["emulator-5554"]
        mock_ios.return_value = ["1111-2222"]

        with self.assertRaises(DeviceNotFoundError):
            resolve_device(device_id="9999")

    @patch('agentic_adb.device_utils._get_android_devices')
    @patch('agentic_adb.device_utils._get_ios_devices')
    def test_resolve_device_override(self, mock_ios, mock_android):
        mock_android.return_value = []
        mock_ios.return_value = []

        device_id, os_type = resolve_device(device_id="123", os_override="android")
        self.assertEqual(device_id, "123")
        self.assertEqual(os_type, "android")

if __name__ == '__main__':
    unittest.main()
