import unittest
import json
from unittest.mock import patch, MagicMock
from mcp_server import get_current_ui, tap_coordinate, swipe_screen, input_text_field

class TestMCPServer(unittest.TestCase):

    @patch('mcp_server.get_services')
    def test_get_current_ui_android(self, mock_get_services):
        mock_query_service = MagicMock()
        mock_action_service = MagicMock()
        mock_get_services.return_value = (mock_query_service, mock_action_service)

        from agentic_adb.models import UIElement
        element = UIElement(index=1, class_name="Button", text="OK", id="btn", desc="", clickable=True, center_x=10, center_y=10)
        mock_query_service.get_ui_elements.return_value = [element]

        result = get_current_ui("android")
        data = json.loads(result)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["text"], "OK")

    @patch('mcp_server.get_services')
    def test_tap_coordinate(self, mock_get_services):
        mock_query_service = MagicMock()
        mock_action_service = MagicMock()
        mock_get_services.return_value = (mock_query_service, mock_action_service)

        result = tap_coordinate("ios", 100, 200)
        self.assertIn("Successfully", result)
        mock_action_service.tap.assert_called_once_with(100, 200)

if __name__ == '__main__':
    unittest.main()
