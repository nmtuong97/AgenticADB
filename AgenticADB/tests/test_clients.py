import unittest
from unittest.mock import patch, MagicMock
from agentic_adb.client import ADBClient, IDBClient
from agentic_adb.exceptions import CommandError

class TestClients(unittest.TestCase):

    @patch('agentic_adb.client.base_client.subprocess.run')
    def test_adb_client_dump(self, mock_run):
        mock_process = MagicMock()
        mock_process.stdout = "<hierarchy></hierarchy>"
        mock_process.check_returncode.return_value = None
        mock_run.return_value = mock_process

        client = ADBClient()
        # Mock tempfile open to avoid actually writing files
        with patch('builtins.open', unittest.mock.mock_open(read_data="<hierarchy></hierarchy>")):
            result = client.dump_ui()

        self.assertEqual(result, "<hierarchy></hierarchy>")
        self.assertEqual(mock_run.call_count, 2)  # One for dump, one for pull

    @patch('agentic_adb.client.base_client.subprocess.run')
    def test_idb_client_dump(self, mock_run):
        mock_process = MagicMock()
        mock_process.stdout = "{}"
        mock_process.check_returncode.return_value = None
        mock_run.return_value = mock_process

        client = IDBClient()
        result = client.dump_ui()

        self.assertEqual(result, "{}")
        mock_run.assert_called_once()

    @patch('agentic_adb.client.base_client.subprocess.run')
    def test_base_client_retry(self, mock_run):
        client = IDBClient()

        # Simulate failure then success
        import subprocess
        mock_process_fail = MagicMock()
        mock_process_fail.check_returncode.side_effect = subprocess.CalledProcessError(1, [])
        mock_process_fail.stderr = "error"

        mock_process_success = MagicMock()
        mock_process_success.check_returncode.return_value = None
        mock_process_success.stdout = "{}"

        mock_run.side_effect = [subprocess.CalledProcessError(1, []), mock_process_success]

        with patch('time.sleep'): # skip sleep in test
            result = client.dump_ui()

        self.assertEqual(result, "{}")
        self.assertEqual(mock_run.call_count, 2)

if __name__ == '__main__':
    unittest.main()
