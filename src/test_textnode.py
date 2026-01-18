import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq2(self):
        node = TextNode("This is a text node", TextType.ITALIC)
        node2 = TextNode("This is a different text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_eq3(self):
        node = TextNode("This is a text node", TextType.LINKS, "https://example.com")
        node2 = TextNode("This is a text node", TextType.LINKS, "https://example.com")
        self.assertEqual(node, node2)

    def test_2nodes_same_text_but_different_type(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.CODE)
        self.assertNotEqual(node, node2)
    
    def test_1node_url_other_url_none(self):
        node = TextNode("This is a text node", TextType.LINKS, "https://example.com")
        node2 = TextNode("This is a text node", TextType.LINKS)
        self.assertNotEqual(node, node2)

    def test_same_text_types_different_urls(self):
        node = TextNode("This is a text node", TextType.LINKS, "https://example1.com")
        node2 = TextNode("This is a text node", TextType.LINKS, "https://example2.com")
        self.assertNotEqual(node, node2)


if __name__ == "__main__":
    unittest.main()