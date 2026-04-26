import unittest
from agentic_adb.parser import ADBParser, IDBParser
from agentic_adb.exceptions import ParseError
from agentic_adb.models import UIElement

class TestParsers(unittest.TestCase):

    def test_ui_element_validation(self):
        with self.assertRaises(ValueError):
            UIElement(1, "Cls", "Txt", "Id", "Desc", True, -1, 0)
        with self.assertRaises(ValueError):
            UIElement(1, "Cls", "Txt", "Id", "Desc", True, 0, -1)

    def test_adb_parser(self):
        parser = ADBParser()
        xml = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
    <node class="android.widget.Button" text="Click Me" bounds="[0,0][100,100]" clickable="true" />
    <node class="android.widget.TextView" text="" desc="Invisible" bounds="[0,0][0,0]" clickable="false" />
    <node class="android.widget.ImageView" resource-id="com.example:id/logo" bounds="[200,200][300,300]" clickable="false" />
</hierarchy>
'''
        elements = parser.parse(xml)
        self.assertEqual(len(elements), 2)  # Second node is skipped

        self.assertEqual(elements[0].class_name, "Button")
        self.assertEqual(elements[0].text, "Click Me")
        self.assertEqual(elements[0].center_x, 50)
        self.assertEqual(elements[0].center_y, 50)
        self.assertTrue(elements[0].clickable)

        self.assertEqual(elements[1].class_name, "ImageView")
        self.assertEqual(elements[1].id, "logo")
        self.assertEqual(elements[1].center_x, 250)
        self.assertEqual(elements[1].center_y, 250)

    def test_adb_parser_empty(self):
        parser = ADBParser()
        with self.assertRaises(ParseError):
            parser.parse("")

    def test_idb_parser(self):
        parser = IDBParser()
        json_data = '''
{
  "type": "XCUIElementTypeButton",
  "AXIdentifier": "login_btn",
  "AXLabel": "Login",
  "traits": ["button"],
  "frame": {"x": 10.0, "y": 20.0, "width": 100.0, "height": 40.0},
  "children": [
    {
      "type": "XCUIElementTypeStaticText",
      "AXValue": "Skip"
    }
  ]
}
'''
        elements = parser.parse(json_data)
        self.assertEqual(len(elements), 2)

        self.assertEqual(elements[0].class_name, "Button")
        self.assertEqual(elements[0].id, "login_btn")
        self.assertTrue(elements[0].clickable)
        self.assertEqual(elements[0].center_x, 60)
        self.assertEqual(elements[0].center_y, 40)

        self.assertEqual(elements[1].class_name, "StaticText")
        self.assertEqual(elements[1].text, "Skip")

    def test_idb_parser_empty(self):
        parser = IDBParser()
        elements = parser.parse("")
        self.assertEqual(len(elements), 0)

if __name__ == '__main__':
    unittest.main()
