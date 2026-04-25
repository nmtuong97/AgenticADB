import unittest
import os
from agentic_adb.parser import parse_xml

class TestParser(unittest.TestCase):

    def setUp(self):
        mock_path = os.path.join(os.path.dirname(__file__), 'mocks', 'mock_ui.xml')
        with open(mock_path, 'r', encoding='utf-8') as f:
            self.xml_content = f.read()

    def test_parse_and_filter(self):
        elements = parse_xml(self.xml_content)

        # 1. The root FrameLayout and LinearLayout should be filtered out
        # 2. ViewGroup with resource-id="submit_button" should be kept
        # 3. TextView with text="Submit" should be kept
        # 4. ViewGroup with content-desc="Close Modal" should be kept
        # 5. EditText with resource-id="username_input" and text="Enter Username" should be kept
        self.assertEqual(len(elements), 4)

        # First valid node (submit_button wrapper)
        elem1 = elements[0]
        self.assertEqual(elem1.index, 1)
        self.assertEqual(elem1.class_name, "ViewGroup")
        self.assertEqual(elem1.id, "submit_button")
        self.assertEqual(elem1.desc, "")
        self.assertTrue(elem1.clickable)
        # bounds="[100,500][980,600]"
        # center_x = (100+980)//2 = 540
        # center_y = (500+600)//2 = 550
        self.assertEqual(elem1.center_x, 540)
        self.assertEqual(elem1.center_y, 550)

        # Second valid node (Submit text)
        elem2 = elements[1]
        self.assertEqual(elem2.index, 2)
        self.assertEqual(elem2.class_name, "TextView")
        self.assertEqual(elem2.text, "Submit")
        self.assertFalse(elem2.clickable)

        # Third valid node (Close Modal)
        elem3 = elements[2]
        self.assertEqual(elem3.index, 3)
        self.assertEqual(elem3.class_name, "ViewGroup")
        self.assertEqual(elem3.desc, "Close Modal")
        self.assertTrue(elem3.clickable)

        # Fourth valid node (Username input)
        elem4 = elements[3]
        self.assertEqual(elem4.index, 4)
        self.assertEqual(elem4.class_name, "EditText")
        self.assertEqual(elem4.id, "username_input")
        self.assertEqual(elem4.text, "Enter Username")

    def test_filter_noise(self):
        # A node with text, desc, id all empty, and clickable=false -> must be excluded
        xml = '''<?xml version='1.0' encoding='UTF-8'?>
        <hierarchy rotation="0">
            <node index="0" text="" resource-id="" class="android.widget.FrameLayout" content-desc="" clickable="false" bounds="[0,0][100,100]" />
        </hierarchy>
        '''
        elements = parse_xml(xml)
        self.assertEqual(len(elements), 0)

    def test_filter_keep_clickable_but_empty(self):
        # A node with text, desc, id all empty, BUT clickable=true -> must be INCLUDED
        xml = '''<?xml version='1.0' encoding='UTF-8'?>
        <hierarchy rotation="0">
            <node index="0" text="" resource-id="" class="android.widget.FrameLayout" content-desc="" clickable="true" bounds="[0,0][100,100]" />
        </hierarchy>
        '''
        elements = parse_xml(xml)
        self.assertEqual(len(elements), 1)

if __name__ == '__main__':
    unittest.main()
