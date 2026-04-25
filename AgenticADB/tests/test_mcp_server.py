import unittest
from unittest.mock import patch
import subprocess
from mcp_server import get_current_ui, tap_coordinate, swipe_screen, input_text_field

class TestMCPServer(unittest.TestCase):

    @patch('mcp_server.get_client')
    def test_get_current_ui_exception_handling(self, mock_get_client):
        # Simulate a subprocess failure by throwing CalledProcessError
        mock_client = mock_get_client.return_value
        mock_client.dump.side_effect = subprocess.CalledProcessError(1, ["adb", "shell"])

        result = get_current_ui("android")

        self.assertTrue(result.startswith("Action failed:"))
        self.assertIn("Command '['adb', 'shell']' returned non-zero exit status 1.", result)

    @patch('mcp_server.get_client')
    def test_tap_coordinate_exception_handling(self, mock_get_client):
        mock_client = mock_get_client.return_value
        mock_client.tap.side_effect = Exception("Device disconnected")

        result = tap_coordinate("ios", 100, 200)

        self.assertTrue(result.startswith("Action failed:"))
        self.assertIn("Device disconnected", result)

    @patch('mcp_server.get_client')
    def test_swipe_screen_exception_handling(self, mock_get_client):
        mock_client = mock_get_client.return_value
        mock_client.swipe.side_effect = Exception("Swipe failed")

        result = swipe_screen("android", 0, 0, 100, 100)

        self.assertTrue(result.startswith("Action failed:"))
        self.assertIn("Swipe failed", result)

    @patch('mcp_server.get_client')
    def test_input_text_field_exception_handling(self, mock_get_client):
        mock_client = mock_get_client.return_value
        mock_client.input_text.side_effect = Exception("Keyboard not shown")

        result = input_text_field("ios", "hello")

        self.assertTrue(result.startswith("Action failed:"))
        self.assertIn("Keyboard not shown", result)

if __name__ == '__main__':
    unittest.main()
