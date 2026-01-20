import unittest

from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHtmlNode(unittest.TestCase):
    
    def test_props_to_html_no_props(self):
        node = HTMLNode(tag="div")
        self.assertEqual(node.props_to_html(), "")
    
    def test_props_to_html_with_props(self):
        props = {"class": "my-class", "id": "my-id"}
        node = HTMLNode(tag="div", props=props)
        expected = ' class="my-class" id="my-id"'
        self.assertEqual(node.props_to_html(), expected)
    
    def test_repr(self):
        props = {"class": "my-class"}
        children = [HTMLNode(tag="span", value="Hello")]
        node = HTMLNode(tag="div", value="Container", children=children, props=props)
        expected = "HTMLNode(div, Container, children: [HTMLNode(span, Hello, children: None, None)], {'class': 'my-class'})"
        self.assertEqual(repr(node), expected)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Just some text")
        self.assertEqual(node.to_html(), "Just some text") 

    def test_leaf_to_html_with_props(self):
        props = {"class": "text-bold"}
        node = LeafNode("span", "Bold Text", props=props)
        self.assertEqual(node.to_html(), '<span class="text-bold">Bold Text</span>')

    def test_leaf_to_html_no_value(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()
    
    def test_leaf_repr(self):
        props = {"style": "color:red;"}
        node = LeafNode("h1", "Title", props=props)
        expected = "LeafNode(h1, Title, {'style': 'color:red;'})"
        self.assertEqual(repr(node), expected)


# tests for parent node

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")


    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
        parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_no_tag(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode(None, [child_node])
        with self.assertRaises(ValueError):
            parent_node.to_html()
    
    def test_to_html_no_children(self):
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_parentnode_with_nested_children(self):
        grandchild1 = LeafNode("i", "italic text")
        grandchild2 = LeafNode("u", "underlined text")
        child = ParentNode("span", [grandchild1, grandchild2])
        parent = ParentNode("div", [child])
        expected_html = "<div><span><i>italic text</i><u>underlined text</u></span></div>"
        self.assertEqual(parent.to_html(), expected_html)

    def test_parentnode_with_multiple_children(self):
        child1 = LeafNode("h2", "Subtitle")
        child2 = LeafNode("p", "This is a paragraph.")
        parent = ParentNode("section", [child1, child2])
        expected_html = "<section><h2>Subtitle</h2><p>This is a paragraph.</p></section>"
        self.assertEqual(parent.to_html(), expected_html)

    def test_parentnode_with_props(self):
        child = LeafNode("p", "Content")
        props = {"class": "container", "id": "main-section"}
        parent = ParentNode("div", [child], props=props)
        expected_html = '<div class="container" id="main-section"><p>Content</p></div>'
        self.assertEqual(parent.to_html(), expected_html)
    
#tests for textnode to htmlnode conversion

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    
    def test_bold(self):
        node = TextNode("Bold Text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold Text")

    def test_italic(self):
        node = TextNode("Italic Text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic Text")
    
    def test_code(self):
        node = TextNode("Code Snippet", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "Code Snippet")
    
    def test_link(self):
        node = TextNode("OpenAI", TextType.LINK, url="https://www.openai.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "OpenAI")
        self.assertEqual(html_node.props, {"href": "https://www.openai.com"})

    def test_image(self):
        node = TextNode("An image", TextType.IMAGE, url="https://www.example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "https://www.example.com/image.png", "alt": "An image"})

    



if __name__ == "__main__":
    unittest.main()