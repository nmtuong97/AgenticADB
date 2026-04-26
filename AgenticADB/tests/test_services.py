import unittest
from unittest.mock import MagicMock
from agentic_adb.service import UIQueryService, UIActionService
from agentic_adb.models import UIElement

class TestServices(unittest.TestCase):

    def test_ui_query_service(self):
        mock_client = MagicMock()
        mock_client.dump_ui.return_value = "raw"

        mock_parser = MagicMock()
        element = UIElement(1, "Cls", "Txt", "Id", "Desc", True, 0, 0)
        mock_parser.parse.return_value = [element]

        service = UIQueryService(mock_client, mock_parser)

        raw = service.get_raw_ui()
        self.assertEqual(raw, "raw")
        mock_client.dump_ui.assert_called_once()

        elements = service.get_ui_elements()
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].text, "Txt")
        mock_parser.parse.assert_called_once_with("raw")

        parsed = service.parse_raw("custom raw")
        self.assertEqual(len(parsed), 1)
        mock_parser.parse.assert_called_with("custom raw")

    def test_ui_query_service_empty(self):
        mock_client = MagicMock()
        mock_client.dump_ui.return_value = ""

        mock_parser = MagicMock()
        service = UIQueryService(mock_client, mock_parser)

        elements = service.get_ui_elements()
        self.assertEqual(len(elements), 0)
        mock_parser.parse.assert_not_called()

        parsed = service.parse_raw("")
        self.assertEqual(len(parsed), 0)
        mock_parser.parse.assert_not_called()

    def test_ui_action_service(self):
        mock_client = MagicMock()
        service = UIActionService(mock_client)

        service.tap(10, 20)
        mock_client.tap.assert_called_once_with(10, 20)

        service.launch_app("com.app")
        mock_client.launch_app.assert_called_once_with("com.app")

if __name__ == '__main__':
    unittest.main()
