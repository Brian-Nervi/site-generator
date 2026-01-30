import unittest

from blocks import BlockType, markdown_to_blocks, block_to_block_type, heading_level, block_type_to_html_tag, markdown_to_html_node, text_to_children
from text_to_markdown import extract_markdown_images, split_nodes_delimiter,extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes
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

#tests for split_nodes_delimiter

    def test_split_nodes_delimiter_no_delimiter(self):
        node = TextNode("Just plain text", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        assert len(result) == 1
        assert result[0].text == "Just plain text"
        assert result[0].text_type == TextType.TEXT

    def test_split_nodes_delimiter_bold_simple(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        assert len(result) == 3
        assert result[0].text == "This is "
        assert result[0].text_type == TextType.TEXT

        assert result[1].text == "bold"
        assert result[1].text_type == TextType.BOLD

        assert result[2].text == " text"
        assert result[2].text_type == TextType.TEXT

    def test_split_nodes_delimiter_multiple_sections(self):
        node = TextNode("a **b** c **d** e", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        assert [n.text for n in result] == ["a ", "b", " c ", "d", " e"]
        assert [n.text_type for n in result] == [
            TextType.TEXT,
            TextType.BOLD,
            TextType.TEXT,
            TextType.BOLD,
            TextType.TEXT,
    ]

    def test_split_nodes_delimiter_skips_non_text(self):
        code_node = TextNode("already code", TextType.CODE)
        text_node = TextNode("`code` here", TextType.TEXT)

        result = split_nodes_delimiter([code_node, text_node], "`", TextType.CODE)

        # first node unchanged
        assert result[0] is code_node

        # second node split
        assert [n.text for n in result[1:]] == ["", "code", " here"] or \
            [n.text for n in result[1:]] == ["code", " here"]
    

#test for extract_markdown_links and images
    
class TestExtractMarkdown(unittest.TestCase):
    def test_single_image(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png")],
            matches,
        )

    def test_multiple_images(self):
        text = (
            "One ![first](https://a.com/1.png) and "
            "two ![second](https://b.com/2.jpg)"
        )
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [
                ("first", "https://a.com/1.png"),
                ("second", "https://b.com/2.jpg"),
            ],
            matches,
        )

    def test_single_link(self):
        text = "A link [to boot dev](https://www.boot.dev)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [("to boot dev", "https://www.boot.dev")],
            matches,
        )

    def test_multiple_links(self):
        text = (
            "Links [one](https://a.com) and "
            "[two](https://b.com/path)"
        )
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [
                ("one", "https://a.com"),
                ("two", "https://b.com/path"),
            ],
            matches,
        )

    def test_images_not_captured_as_links(self):
        text = "![pic](https://a.com/pic.png)"
        matches = extract_markdown_links(text)
        self.assertListEqual([], matches)

    def test_mixed_links_and_images(self):
        text = (
            "![img](https://a.com/img.png) and "
            "[anchor](https://a.com)"
        )
        img_matches = extract_markdown_images(text)
        link_matches = extract_markdown_links(text)
        self.assertListEqual(
            [("img", "https://a.com/img.png")],
            img_matches,
        )
        self.assertListEqual(
            [("anchor", "https://a.com")],
            link_matches,
        )

# tests for split_nodes_image and split_nodes_link

    def split_nodes_link(old_nodes):
        new_nodes = []
        for node in old_nodes:
            if node.text_type != TextType.TEXT:
                new_nodes.append(node)
                continue
            original_text = node.text
            links = extract_markdown_links(original_text)
            if len(links) == 0:
                new_nodes.append(node)
                continue
            for link in links:
                text = link[0]
                url = link[1]
                sections = original_text.split(f"[{text}]({url})", 1)
                if sections[0] != "":
                    new_nodes.append(TextNode(sections[0], TextType.TEXT))
                new_nodes.append(TextNode(text, TextType.LINK, url))
                original_text = sections[1]
            if original_text != "":
                new_nodes.append(TextNode(original_text, TextType.TEXT))
        return new_nodes

    def test_split_images_single(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )


    def test_split_images_multiple(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image",
                    TextType.IMAGE,
                    "https://i.imgur.com/3elNhQu.png",
                ),
            ],
            new_nodes,
        )


    def test_split_images_no_image(self):
        node = TextNode("Just boring text", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links_single(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            ],
            new_nodes,
        )


    def test_split_links_multiple(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube",
                    TextType.LINK,
                    "https://www.youtube.com/@bootdotdev",
                ),
            ],
            new_nodes,
        )


    def test_split_links_no_link(self):
        node = TextNode("Just boring text", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

# tests for text_to_textnodes

class TestTextToTextNodes(unittest.TestCase):
    def test_simple_mixed_formatting(self):
        text = "This is **bold** and *italic* text with `code`."
        nodes = text_to_textnodes(text)

        # Just check key nodes in order
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertIn("This is", nodes[0].text)

        self.assertEqual(nodes[1].text, "bold")
        self.assertEqual(nodes[1].text_type, TextType.BOLD)

        self.assertEqual(nodes[2].text_type, TextType.TEXT)
        self.assertIn("italic", "".join(n.text for n in nodes))

        self.assertTrue(any(n.text == "code" and n.text_type == TextType.CODE for n in nodes))
    def test_links_and_images(self):
        text = (
            "This is an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) "
            "and a [link](https://boot.dev)"
        )
        nodes = text_to_textnodes(text)

        expected_texts = [
            "This is an ",
            "obi wan image",
            " and a ",
            "link",
        ]
        expected_types = [
            TextType.TEXT,
            TextType.IMAGE,
            TextType.TEXT,
            TextType.LINK,
        ]
        expected_urls = [
            None,
            "https://i.imgur.com/fJRm4Vk.jpeg",
            None,
            "https://boot.dev",
        ]

        self.assertEqual(len(nodes), len(expected_texts))
        for node, exp_text, exp_type, exp_url in zip(
            nodes, expected_texts, expected_types, expected_urls
        ):
            self.assertEqual(node.text, exp_text)
            self.assertEqual(node.text_type, exp_type)
            self.assertEqual(node.url, exp_url)

    def test_no_formatting(self):
        text = "Just boring text."
        nodes = text_to_textnodes(text)

        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, text)
        self.assertEqual(nodes[0].text_type, TextType.TEXT)

    def test_only_code(self):
        text = "`code`"
        nodes = text_to_textnodes(text)

        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, "code")
        self.assertEqual(nodes[0].text_type, TextType.CODE)

    def test_multiple_same_format(self):
        text = "**bold1** and **bold2**"
        nodes = text_to_textnodes(text)

        expected_texts = [
            "bold1",
            " and ",
            "bold2",
        ]
        expected_types = [
            TextType.BOLD,
            TextType.TEXT,
            TextType.BOLD,
        ]

        self.assertEqual(len(nodes), len(expected_texts))
        for node, exp_text, exp_type in zip(nodes, expected_texts, expected_types):
            self.assertEqual(node.text, exp_text)
            self.assertEqual(node.text_type, exp_type)

# test for blocks.py

    def test_markdown_to_blocks(self):
            md = """
        This is **bolded** paragraph

        This is another paragraph with _italic_ text and `code` here
        This is the same paragraph on a new line

        - This is a list
        - with items
        """
            blocks = markdown_to_blocks(md)
            self.assertEqual(
                blocks,
                    [
                        "This is **bolded** paragraph",
                        "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                        "- This is a list\n- with items",
                    ],
                )






    def test_markdown_to_blocks_example(self):
            md = """
    This is **bolded** paragraph

    This is another paragraph with _italic_ text and `code` here
    This is the same paragraph on a new line

    - This is a list
    - with items
    """
            blocks = markdown_to_blocks(md)
            self.assertEqual(
                blocks,
                [
                    "This is **bolded** paragraph",
                    "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                    "- This is a list\n- with items",
                ],
            )

    def test_leading_and_trailing_blank_lines(self):
            md = """

    First paragraph

    Second paragraph

    """
            blocks = markdown_to_blocks(md)
            self.assertEqual(
                blocks,
                ["First paragraph", "Second paragraph"],
            )

    def test_multiple_blank_lines(self):
            md = """Line one


    Line two



    Line three"""
            blocks = markdown_to_blocks(md)
            self.assertEqual(
                blocks,
                ["Line one", "Line two", "Line three"],
            )
    def test_single_block_no_blank_lines(self):
            md = "Only one block\nwith two lines"
            blocks = markdown_to_blocks(md)
            self.assertEqual(
                blocks,
                ["Only one block\nwith two lines"],
            )

# test for block_to_block_type

    def test_paragraph_simple(self):
        block = "This is a simple paragraph."
        assert block_to_block_type(block) == BlockType.paragraph


    def test_heading_levels_1_to_6(self):
        for level in range(1, 7):
            hashes = "#" * level
            block = f"{hashes} Heading level {level}"
            assert block_to_block_type(block) == BlockType.heading

    def test_heading_not_valid_without_space(self):
        block = "###No space after hashes"
        assert block_to_block_type(block) == BlockType.paragraph

    def test_code_block_simple(self):
        block = "```\nprint('hi')\n```"
        assert block_to_block_type(block) == BlockType.code

    def test_code_block_with_language_tag(self):
        block = "```python\nprint('hi')\n```"
        assert block_to_block_type(block) == BlockType.code

    def test_code_block_single_line_not_code(self):
        block = "```print('hi')```"
        assert block_to_block_type(block) == BlockType.paragraph

    def test_quote_single_line(self):
        block = "> hello there"
        assert block_to_block_type(block) == BlockType.quote

    def test_quote_multi_line_all_prefixed(self):
        block = "> first line\n> second line"
        assert block_to_block_type(block) == BlockType.quote

    def test_quote_with_bad_line_becomes_paragraph(self):
        block = "> first line\nsecond line"
        assert block_to_block_type(block) == BlockType.paragraph

    def test_unordered_list_single_line(self):
        block = "- item one"
        assert block_to_block_type(block) == BlockType.unordered_list

    def test_unordered_list_multi_line_all_prefixed(self):
        block = "- item one\n- item two\n- item three"
        assert block_to_block_type(block) == BlockType.unordered_list

    def test_unordered_list_with_bad_line_becomes_paragraph(self):
        block = "- item one\nitem two"
        assert block_to_block_type(block) == BlockType.paragraph

    def test_ordered_list_correct_sequence(self):
        block = "1. first\n2. second\n3. third"
        assert block_to_block_type(block) == BlockType.ordered_list

    def test_ordered_list_wrong_start_number_becomes_paragraph(self):
        block = "2. first\n3. second"
        assert block_to_block_type(block) == BlockType.paragraph

    def test_ordered_list_wrong_increment_becomes_paragraph(self):
        block = "1. first\n3. second"
        assert block_to_block_type(block) == BlockType.paragraph

    def test_ordered_list_single_item(self):
        block = "1. only item"
        assert block_to_block_type(block) == BlockType.ordered_list

class TestMarkdownToHtmlNodeCustom(unittest.TestCase):
    def test_simple_paragraph(self):
        md = "This is **bold** and *italic*."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bold</b> and <i>italic</i>.</p></div>",
        )

    def test_multiple_paragraphs(self):
        md = """
            This is first paragraph

            This is second paragraph
            """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is first paragraph</p><p>This is second paragraph</p></div>",
        )

    def test_heading_levels(self):
        md = """
            # Title
            ## Subtitle
            ### Subsubtitle
            """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Title</h1><h2>Subtitle</h2><h3>Subsubtitle</h3></div>",
        )

    def test_code_block_no_inline(self):
        md = """
        ```
        This is text that _should_ remain
        the **same** even with inline stuff
        ```
    """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_unordered_list(self):
        md = """
            - first **item**
            - second item with *style*
            """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>first <b>item</b></li><li>second item with <i>style</i></li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
            1. first
            2. second `code`
            3. third
            """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>first</li><li>second <code>code</code></li><li>third</li></ol></div>",
        )

    def test_quote_block(self):
        md = """
            > this is **quoted**
            > text
            """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>this is <b>quoted</b> text</blockquote></div>",
        )

if __name__ == "__main__":
    unittest.main()

if __name__ == "__main__":
    unittest.main()