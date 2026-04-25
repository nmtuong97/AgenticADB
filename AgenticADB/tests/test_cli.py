import unittest
from unittest.mock import patch
from agentic_adb.cli import run_cli

class TestCLI(unittest.TestCase):

    @patch('agentic_adb.cli.parse_xml')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_android(self, mock_adb_class, mock_parse_xml):
        mock_client = mock_adb_class.return_value
        mock_client.dump.return_value = "<hierarchy></hierarchy>"
        mock_parse_xml.return_value = []

        run_cli(["--os", "android"])

        mock_adb_class.assert_called_once()
        mock_client.dump.assert_called_once()
        mock_parse_xml.assert_called_once_with("<hierarchy></hierarchy>")

    @patch('agentic_adb.cli.parse_idb_json')
    @patch('agentic_adb.cli.IDBClient')
    def test_cli_ios(self, mock_idb_class, mock_parse_idb):
        mock_client = mock_idb_class.return_value
        mock_client.dump.return_value = "{}"
        mock_parse_idb.return_value = []

        run_cli(["--os", "ios"])

        mock_idb_class.assert_called_once()
        mock_client.dump.assert_called_once()
        mock_parse_idb.assert_called_once_with("{}")

if __name__ == '__main__':
    unittest.main()
