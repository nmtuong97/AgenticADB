import unittest
from unittest.mock import patch
from agentic_adb.cli import run_cli

class TestCLI(unittest.TestCase):

    @patch('agentic_adb.cli.resolve_device')
    @patch('agentic_adb.cli.UIQueryService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_android_dump(self, mock_adb_class, mock_parser_class, mock_query_service_class, mock_resolve):
        mock_resolve.return_value = ("device_123", "android")
        mock_client = mock_adb_class.return_value
        mock_parser = mock_parser_class.return_value
        mock_query_service = mock_query_service_class.return_value
        mock_query_service.get_raw_ui.return_value = "<hierarchy></hierarchy>"
        mock_query_service.parse_raw.return_value = []

        run_cli(["--os", "android", "dump"])

        mock_resolve.assert_called_once_with(None, "android")
        mock_adb_class.assert_called_once_with(device_id="device_123")
        mock_parser_class.assert_called_once()
        mock_query_service_class.assert_called_once_with(client=mock_client, parser=mock_parser)
        mock_query_service.get_raw_ui.assert_called_once()
        mock_query_service.parse_raw.assert_called_once_with("<hierarchy></hierarchy>")

    @patch('agentic_adb.cli.resolve_device')
    @patch('agentic_adb.cli.UIQueryService')
    @patch('agentic_adb.cli.IDBParser')
    @patch('agentic_adb.cli.IDBClient')
    def test_cli_ios_dump(self, mock_idb_class, mock_parser_class, mock_query_service_class, mock_resolve):
        mock_resolve.return_value = ("ios_456", "ios")
        mock_client = mock_idb_class.return_value
        mock_parser = mock_parser_class.return_value
        mock_query_service = mock_query_service_class.return_value
        mock_query_service.get_raw_ui.return_value = "{}"
        mock_query_service.parse_raw.return_value = []

        run_cli(["--device", "ios_456", "dump"])

        mock_resolve.assert_called_once_with("ios_456", None)
        mock_idb_class.assert_called_once_with(device_id="ios_456")
        mock_parser_class.assert_called_once()
        mock_query_service_class.assert_called_once_with(client=mock_client, parser=mock_parser)
        mock_query_service.get_raw_ui.assert_called_once()
        mock_query_service.parse_raw.assert_called_once_with("{}")

    @patch('agentic_adb.cli.sys.exit')
    @patch('agentic_adb.cli.sys.stderr.write')
    @patch('agentic_adb.cli.resolve_device')
    @patch('agentic_adb.cli.UIQueryService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_command_error(self, mock_adb_class, mock_parser_class, mock_query_service_class, mock_resolve, mock_stderr, mock_exit):
        from agentic_adb.exceptions import CommandError
        mock_resolve.return_value = ("dev1", "android")
        mock_query_service = mock_query_service_class.return_value
        mock_query_service.get_raw_ui.side_effect = CommandError("Device error")

        run_cli(["dump"])

        mock_exit.assert_called_once_with(1)
        mock_stderr.assert_called_once_with("Error communicating with device: Device error\n")

    @patch('agentic_adb.cli.sys.exit')
    @patch('agentic_adb.cli.sys.stderr.write')
    @patch('agentic_adb.cli.resolve_device')
    @patch('agentic_adb.cli.UIQueryService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_parse_error(self, mock_adb_class, mock_parser_class, mock_query_service_class, mock_resolve, mock_stderr, mock_exit):
        from agentic_adb.exceptions import ParseError
        mock_resolve.return_value = ("dev1", "android")
        mock_query_service = mock_query_service_class.return_value
        mock_query_service.get_raw_ui.return_value = "raw"
        mock_query_service.parse_raw.side_effect = ParseError("Malformed data")

        run_cli(["dump"])

        mock_exit.assert_called_once_with(1)
        mock_stderr.assert_called_once_with("Error parsing UI elements: Malformed data\n")

    @patch('agentic_adb.cli.resolve_device')
    @patch('agentic_adb.cli.UIActionService')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_action_tap(self, mock_adb_class, mock_action_service_class, mock_resolve):
        mock_resolve.return_value = ("dev1", "android")
        mock_action_service = mock_action_service_class.return_value

        run_cli(["tap", "--x", "100", "--y", "200"])

        mock_resolve.assert_called_once_with(None, None)
        mock_action_service_class.assert_called_once()
        mock_action_service.tap.assert_called_once_with(100, 200)

    @patch('agentic_adb.cli.sys.exit')
    @patch('agentic_adb.cli.sys.stderr.write')
    @patch('agentic_adb.cli.resolve_device')
    def test_cli_resolve_error(self, mock_resolve, mock_stderr, mock_exit):
        from agentic_adb.exceptions import DeviceNotFoundError
        mock_resolve.side_effect = DeviceNotFoundError("No devices connected")

        run_cli(["dump"])

        mock_exit.assert_called_once_with(1)
        mock_stderr.assert_called_once_with("Device routing error: No devices connected\n")

if __name__ == '__main__':
    unittest.main()
