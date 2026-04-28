import unittest
from unittest.mock import patch
from agentic_adb.cli import run_cli

class TestCLI(unittest.TestCase):

    @patch('agentic_adb.cli.UIQueryService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_dump_android(self, mock_adb_class, mock_parser_class, mock_query_service_class):
        mock_client = mock_adb_class.return_value
        mock_parser = mock_parser_class.return_value
        mock_query_service = mock_query_service_class.return_value
        mock_query_service.get_raw_ui.return_value = "<hierarchy></hierarchy>"
        mock_query_service.parse_raw.return_value = []

        run_cli(["--os", "android", "dump"])

        mock_adb_class.assert_called_once()
        mock_parser_class.assert_called_once()
        mock_query_service_class.assert_called_once_with(client=mock_client, parser=mock_parser)
        mock_query_service.get_raw_ui.assert_called_once()
        mock_query_service.parse_raw.assert_called_once_with("<hierarchy></hierarchy>")

    @patch('agentic_adb.cli.UIQueryService')
    @patch('agentic_adb.cli.IDBParser')
    @patch('agentic_adb.cli.IDBClient')
    def test_cli_dump_ios(self, mock_idb_class, mock_parser_class, mock_query_service_class):
        mock_client = mock_idb_class.return_value
        mock_parser = mock_parser_class.return_value
        mock_query_service = mock_query_service_class.return_value
        mock_query_service.get_raw_ui.return_value = "{}"
        mock_query_service.parse_raw.return_value = []

        run_cli(["--os", "ios", "dump"])

        mock_idb_class.assert_called_once()
        mock_parser_class.assert_called_once()
        mock_query_service_class.assert_called_once_with(client=mock_client, parser=mock_parser)
        mock_query_service.get_raw_ui.assert_called_once()
        mock_query_service.parse_raw.assert_called_once_with("{}")

    @patch('agentic_adb.cli.UIActionService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_tap(self, mock_adb_class, mock_parser_class, mock_action_service_class):
        mock_client = mock_adb_class.return_value
        mock_action_service = mock_action_service_class.return_value

        run_cli(["--os", "android", "tap", "--x", "100", "--y", "200"])

        mock_action_service_class.assert_called_once_with(client=mock_client)
        mock_action_service.tap.assert_called_once_with(100, 200)

    @patch('agentic_adb.cli.UIActionService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_swipe(self, mock_adb_class, mock_parser_class, mock_action_service_class):
        mock_client = mock_adb_class.return_value
        mock_action_service = mock_action_service_class.return_value

        run_cli(["--os", "android", "swipe", "--x1", "10", "--y1", "20", "--x2", "30", "--y2", "40", "--duration", "800"])

        mock_action_service_class.assert_called_once_with(client=mock_client)
        mock_action_service.swipe.assert_called_once_with(10, 20, 30, 40, 800)

    @patch('agentic_adb.cli.UIActionService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_input(self, mock_adb_class, mock_parser_class, mock_action_service_class):
        mock_client = mock_adb_class.return_value
        mock_action_service = mock_action_service_class.return_value

        run_cli(["--os", "android", "input", "hello world"])

        mock_action_service_class.assert_called_once_with(client=mock_client)
        mock_action_service.input_text.assert_called_once_with("hello world")

    @patch('agentic_adb.cli.UIActionService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_long_press(self, mock_adb_class, mock_parser_class, mock_action_service_class):
        mock_client = mock_adb_class.return_value
        mock_action_service = mock_action_service_class.return_value

        run_cli(["--os", "android", "long_press", "--x", "150", "--y", "250", "--duration", "2000"])

        mock_action_service_class.assert_called_once_with(client=mock_client)
        mock_action_service.long_press.assert_called_once_with(150, 250, 2000)

    @patch('agentic_adb.cli.UIActionService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_press(self, mock_adb_class, mock_parser_class, mock_action_service_class):
        mock_client = mock_adb_class.return_value
        mock_action_service = mock_action_service_class.return_value

        run_cli(["--os", "android", "press", "home"])

        mock_action_service_class.assert_called_once_with(client=mock_client)
        mock_action_service.press_keycode.assert_called_once_with("home")

    @patch('agentic_adb.cli.UIActionService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_launch(self, mock_adb_class, mock_parser_class, mock_action_service_class):
        mock_client = mock_adb_class.return_value
        mock_action_service = mock_action_service_class.return_value

        run_cli(["--os", "android", "launch", "com.example.app"])

        mock_action_service_class.assert_called_once_with(client=mock_client)
        mock_action_service.launch_app.assert_called_once_with("com.example.app")

    @patch('agentic_adb.cli.UIActionService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_kill(self, mock_adb_class, mock_parser_class, mock_action_service_class):
        mock_client = mock_adb_class.return_value
        mock_action_service = mock_action_service_class.return_value

        run_cli(["--os", "android", "kill", "com.example.app"])

        mock_action_service_class.assert_called_once_with(client=mock_client)
        mock_action_service.kill_app.assert_called_once_with("com.example.app")

    @patch('agentic_adb.cli.sys.exit')
    @patch('agentic_adb.cli.sys.stderr.write')
    @patch('agentic_adb.cli.UIQueryService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_command_error(self, mock_adb_class, mock_parser_class, mock_query_service_class, mock_stderr, mock_exit):
        from agentic_adb.exceptions import CommandError
        mock_query_service = mock_query_service_class.return_value
        mock_query_service.get_raw_ui.side_effect = CommandError("Device error")

        run_cli(["--os", "android", "dump"])

        mock_exit.assert_called_once_with(1)
        mock_stderr.assert_called_once_with("Error communicating with device: Device error\n")

    @patch('agentic_adb.cli.sys.exit')
    @patch('agentic_adb.cli.sys.stderr.write')
    @patch('agentic_adb.cli.UIQueryService')
    @patch('agentic_adb.cli.ADBParser')
    @patch('agentic_adb.cli.ADBClient')
    def test_cli_parse_error(self, mock_adb_class, mock_parser_class, mock_query_service_class, mock_stderr, mock_exit):
        from agentic_adb.exceptions import ParseError
        mock_query_service = mock_query_service_class.return_value
        mock_query_service.get_raw_ui.return_value = "raw"
        mock_query_service.parse_raw.side_effect = ParseError("Malformed data")

        run_cli(["--os", "android", "dump"])

        mock_exit.assert_called_once_with(1)
        mock_stderr.assert_called_once_with("Error parsing UI elements: Malformed data\n")

if __name__ == '__main__':
    unittest.main()
