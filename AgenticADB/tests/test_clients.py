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
        mock_run.assert_called_with(["adb", "shell", "input", "tap", "100", "200"], capture_output=True, text=True)

    @patch('agentic_adb.idb_client.subprocess.run')
    def test_idb_client_dump(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "dummy json content"
        mock_run.return_value = mock_result

        client = IDBClient()
        result = client.dump()
        self.assertEqual(result, "dummy json content")
        mock_run.assert_called_with(["idb", "ui", "describe-all"], capture_output=True, text=True)

    @patch('agentic_adb.idb_client.subprocess.run')
    def test_idb_client_swipe(self, mock_run):
        client = IDBClient()
        client.swipe(100, 200, 300, 400, duration_ms=500)
        # IDBClient ignores duration internally
        mock_run.assert_called_with(["idb", "ui", "swipe", "100", "200", "300", "400"], capture_output=True, text=True)


if __name__ == '__main__':
    unittest.main()
