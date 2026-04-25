import unittest
from unittest.mock import patch, MagicMock
from agentic_adb.adb_client import ADBClient
from agentic_adb.idb_client import IDBClient
import subprocess

class TestClients(unittest.TestCase):

    @patch('agentic_adb.adb_client.subprocess.run')
    def test_adb_client_dump(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "dummy xml content"
        mock_run.return_value = mock_result

        # Also need to mock open since dump uses NamedTemporaryFile
        with patch('builtins.open', unittest.mock.mock_open(read_data="dummy xml content")):
            client = ADBClient()
            result = client.dump()
            self.assertEqual(result, "dummy xml content")

            # verify pull command ran
            self.assertTrue(mock_run.called)

    @patch('agentic_adb.adb_client.subprocess.run')
    def test_adb_client_tap(self, mock_run):
        client = ADBClient()
        client.tap(100, 200)
        mock_run.assert_called_with(["adb", "shell", "input", "tap", "100", "200"], capture_output=True, text=True, timeout=15)

    @patch('agentic_adb.idb_client.subprocess.run')
    def test_idb_client_dump(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "dummy json content"
        mock_run.return_value = mock_result

        client = IDBClient()
        result = client.dump()
        self.assertEqual(result, "dummy json content")
        mock_run.assert_called_with(["idb", "ui", "describe-all"], capture_output=True, text=True, timeout=15)

    @patch('agentic_adb.idb_client.subprocess.run')
    def test_idb_client_swipe(self, mock_run):
        client = IDBClient()
        client.swipe(100, 200, 300, 400, duration_ms=500)
        # IDBClient ignores duration internally
        mock_run.assert_called_with(["idb", "ui", "swipe", "100", "200", "300", "400"], capture_output=True, text=True, timeout=15)

    @patch('agentic_adb.adb_client.subprocess.run')
    def test_adb_client_long_press(self, mock_run):
        client = ADBClient()
        client.long_press(100, 200, 1500)
        mock_run.assert_called_with(["adb", "shell", "input", "swipe", "100", "200", "100", "200", "1500"], capture_output=True, text=True, timeout=15)

    @patch('agentic_adb.adb_client.subprocess.run')
    def test_adb_client_press_keycode(self, mock_run):
        client = ADBClient()
        client.press_keycode("home")
        mock_run.assert_called_with(["adb", "shell", "input", "keyevent", "KEYCODE_HOME"], capture_output=True, text=True, timeout=15)

    @patch('agentic_adb.adb_client.subprocess.run')
    def test_adb_client_launch_app(self, mock_run):
        client = ADBClient()
        client.launch_app("com.example.app")
        mock_run.assert_called_with(["adb", "shell", "monkey", "-p", "com.example.app", "-c", "android.intent.category.LAUNCHER", "1"], capture_output=True, text=True, timeout=15)

    @patch('agentic_adb.adb_client.subprocess.run')
    def test_adb_client_kill_app(self, mock_run):
        client = ADBClient()
        client.kill_app("com.example.app")
        mock_run.assert_called_with(["adb", "shell", "am", "force-stop", "com.example.app"], capture_output=True, text=True, timeout=15)

    @patch('agentic_adb.idb_client.subprocess.run')
    def test_idb_client_long_press(self, mock_run):
        client = IDBClient()
        client.long_press(100, 200, 1500)
        mock_run.assert_called_with(["idb", "ui", "swipe", "100", "200", "100", "200", "--duration", "1.5"], capture_output=True, text=True, timeout=15)

    @patch('agentic_adb.idb_client.subprocess.run')
    def test_idb_client_press_keycode(self, mock_run):
        client = IDBClient()

        client.press_keycode("home")
        mock_run.assert_called_with(["idb", "ui", "button", "HOME"], capture_output=True, text=True, timeout=15)

        client.press_keycode("enter")
        mock_run.assert_called_with(["idb", "ui", "text", "\n"], capture_output=True, text=True, timeout=15)

        result = client.press_keycode("back")
        self.assertTrue(result.startswith("Warning"))

    @patch('agentic_adb.idb_client.subprocess.run')
    def test_idb_client_launch_app(self, mock_run):
        client = IDBClient()
        client.launch_app("com.example.app")
        mock_run.assert_called_with(["idb", "launch", "com.example.app"], capture_output=True, text=True, timeout=15)

    @patch('agentic_adb.idb_client.subprocess.run')
    def test_idb_client_kill_app(self, mock_run):
        client = IDBClient()
        client.kill_app("com.example.app")
        mock_run.assert_called_with(["idb", "terminate", "com.example.app"], capture_output=True, text=True, timeout=15)

    @patch('agentic_adb.adb_client.subprocess.run')
    @patch('agentic_adb.adb_client.time.sleep')
    def test_adb_client_retry_logic(self, mock_sleep, mock_run):
        client = ADBClient()
        # Make run raise TimeoutExpired first 2 times, then succeed
        mock_run.side_effect = [
            subprocess.TimeoutExpired(["adb"], 15),
            subprocess.TimeoutExpired(["adb"], 15),
            MagicMock(stdout="success")
        ]

        client.tap(100, 200)
        self.assertEqual(mock_run.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)


if __name__ == '__main__':
    unittest.main()
