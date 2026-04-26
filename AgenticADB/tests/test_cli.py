import unittest
from unittest.mock import patch
from agentic_adb.cli import run_cli

class TestCLI(unittest.TestCase):

    @patch('agentic_adb.cli.UIQueryService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_android(self, mock_adb_class, mock_parser_class, mock_query_service_class):
        mock_client = mock_adb_class.return_value
        mock_parser = mock_parser_class.return_value
        mock_query_service = mock_query_service_class.return_value
        mock_query_service.get_raw_ui.return_value = "<hierarchy></hierarchy>"
        mock_query_service.parse_raw.return_value = []

        run_cli(["--os", "android"])

        mock_adb_class.assert_called_once()
        mock_parser_class.assert_called_once()
        mock_query_service_class.assert_called_once_with(client=mock_client, parser=mock_parser)
        mock_query_service.get_raw_ui.assert_called_once()
        mock_query_service.parse_raw.assert_called_once_with("<hierarchy></hierarchy>")

    @patch('agentic_adb.cli.UIQueryService')
    @patch('agentic_adb.cli.IDBParser')
    @patch('agentic_adb.cli.IDBClient')
    def test_cli_ios(self, mock_idb_class, mock_parser_class, mock_query_service_class):
        mock_client = mock_idb_class.return_value
        mock_parser = mock_parser_class.return_value
        mock_query_service = mock_query_service_class.return_value
        mock_query_service.get_raw_ui.return_value = "{}"
        mock_query_service.parse_raw.return_value = []

        run_cli(["--os", "ios"])

        mock_idb_class.assert_called_once()
        mock_parser_class.assert_called_once()
        mock_query_service_class.assert_called_once_with(client=mock_client, parser=mock_parser)
        mock_query_service.get_raw_ui.assert_called_once()
        mock_query_service.parse_raw.assert_called_once_with("{}")

if __name__ == '__main__':
    unittest.main()
