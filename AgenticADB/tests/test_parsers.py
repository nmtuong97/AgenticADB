import unittest
import os
from agentic_adb.parser import parse_xml
from agentic_adb.idb_parser import parse_idb_json

class TestParsers(unittest.TestCase):

    def setUp(self):
        android_mock_path = os.path.join(os.path.dirname(__file__), 'mocks', 'mock_android_dump.xml')
        with open(android_mock_path, 'r', encoding='utf-8') as f:
            self.android_xml = f.read()

        ios_mock_path = os.path.join(os.path.dirname(__file__), 'mocks', 'mock_ios_dump.json')
        with open(ios_mock_path, 'r', encoding='utf-8') as f:
            self.ios_json = f.read()

    def test_android_parser(self):
        elements = parse_xml(self.android_xml)

        self.assertEqual(len(elements), 3, "There should be exactly 3 elements after filtering.")

        # Element 1: Valid standard node
        elem1 = elements[0]
        self.assertEqual(elem1.class_name, "TextView")
        self.assertEqual(elem1.text, "Submit")
        self.assertEqual(elem1.center_x, 125) # (100+150)//2
        self.assertEqual(elem1.center_y, 225) # (200+250)//2
        self.assertFalse(elem1.clickable)

        # Element 2: React Native touchable
        elem2 = elements[1]
        self.assertEqual(elem2.class_name, "ViewGroup")
        self.assertEqual(elem2.id, "login_btn") # Prefix stripped
        self.assertEqual(elem2.text, "")
        self.assertEqual(elem2.center_x, 20) # (10+30)//2
        self.assertEqual(elem2.center_y, 30) # (20+40)//2
        self.assertTrue(elem2.clickable)

        # Element 3: Prefix stripping
        elem3 = elements[2]
        self.assertEqual(elem3.class_name, "Button")
        self.assertEqual(elem3.id, "my_btn") # Prefix stripped
        self.assertEqual(elem3.center_x, 350)
        self.assertEqual(elem3.center_y, 450)
        self.assertTrue(elem3.clickable)


    def test_ios_parser(self):
        elements = parse_idb_json(self.ios_json)

        self.assertEqual(len(elements), 4, "There should be exactly 4 elements after filtering.")

        # Application node - root
        elem1 = elements[0]
        self.assertEqual(elem1.class_name, "Application")
        self.assertEqual(elem1.id, "com.apple.Preferences")
        self.assertEqual(elem1.desc, "Settings")
        self.assertFalse(elem1.clickable)

        # Button node with frame math
        elem2 = elements[1]
        self.assertEqual(elem2.class_name, "Button")
        self.assertEqual(elem2.id, "login_btn")
        self.assertEqual(elem2.desc, "Login")
        self.assertEqual(elem2.center_x, 125) # x + width/2 = 100 + 25
        self.assertEqual(elem2.center_y, 225) # y + height/2 = 200 + 25
        self.assertTrue(elem2.clickable)

        # Touchable without text (empty AXLabel/AXValue, but traits=["button"])
        elem3 = elements[2]
        self.assertEqual(elem3.class_name, "Other")
        self.assertEqual(elem3.text, "")
        self.assertEqual(elem3.id, "")
        self.assertTrue(elem3.clickable)

        # Static Text (prefix stripped)
        elem4 = elements[3]
        self.assertEqual(elem4.class_name, "StaticText")
        self.assertEqual(elem4.id, "welcome_text")
        self.assertEqual(elem4.desc, "Welcome")
        self.assertFalse(elem4.clickable)

if __name__ == '__main__':
    unittest.main()
