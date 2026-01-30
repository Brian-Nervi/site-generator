from enum import Enum
from htmlnode import ParentNode, LeafNode
from textnode import TextNode, TextType
from text_to_markdown import split_nodes_delimiter, split_nodes_image, split_nodes_link
from textnode import text_node_to_html_node

class BlockType(Enum):
    paragraph = "paragraph"
    heading = "heading"
    code = "code"
    quote = "quote"
    unordered_list = "unordered_list"
    ordered_list = "ordered_list"

def block_to_block_type(block):
    lines = block.split("\n")
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.heading
    elif len(lines) > 1 and lines[0].lstrip().startswith("```") and lines[-1].lstrip().startswith("```"):
        return BlockType.code
    elif block.startswith("> "):
        for line in lines:
            if not line.startswith("> "):
                return BlockType.paragraph
        return BlockType.quote
    elif block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.paragraph
        return BlockType.unordered_list
    elif block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.paragraph
            i += 1
        return BlockType.ordered_list
    else:
        return BlockType.paragraph



def markdown_to_blocks(markdown):
    blocks = []
    lines = markdown.split("\n")
    current_block = []    
    for line in lines:
        if line.strip() == "":
            if current_block:
                blocks.append("\n".join(current_block).strip())
                current_block = []
        elif line.lstrip().startswith(("# ","## ","### ","#### ","##### ","###### ")):
            if current_block:
                blocks.append("\n".join(current_block).strip())
                current_block = []
            current_block.append(line.strip())
        else:
            current_block.append(line.strip())
    if current_block:
        blocks.append("\n".join(current_block).strip())
    return blocks


def block_type_to_html_tag(block_type):
    if block_type == BlockType.paragraph:
        return "p"
    elif block_type == BlockType.heading:
        return "h2"
    elif block_type == BlockType.quote:
        return "blockquote"
    elif block_type == BlockType.unordered_list:
        return "ul"
    elif block_type == BlockType.ordered_list:
        return "ol"
    elif block_type == BlockType.code:
        return "pre"
    else:
        raise Exception(f"Unknown BlockType: {block_type}")
    
def text_to_children(text):
    

    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

    html_nodes = [text_node_to_html_node(node) for node in nodes]
    return html_nodes

def heading_level(markdown):
    if markdown.startswith("###### "):
        return 6
    elif markdown.startswith("##### "):
        return 5
    elif markdown.startswith("#### "):
        return 4
    elif markdown.startswith("### "):
        return 3
    elif markdown.startswith("## "):
        return 2
    elif markdown.startswith("# "):
        return 1
    

    



def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    html_nodes = []
    for block in blocks:       
        block_type = block_to_block_type(block)
        if block_type == BlockType.code:
            inner_lines = block.split("\n")[1:-1]
            code_text = "\n".join(inner_lines) + "\n"
            html_nodes.append(
            ParentNode(
                tag="pre",
                children=[LeafNode("code", code_text)],
            )
         )
        elif block_type == BlockType.heading:
            level = heading_level(block)
            html_nodes.append(
                ParentNode(
                    tag=f"h{level}",
                    children=text_to_children(block[level + 1 :].strip())
                )
            )
        elif block_type == BlockType.unordered_list:
            list_items = []
            for line in block.split("\n"):
                item_text = line[2:].strip()
                list_items.append(
                    ParentNode(
                        tag="li",
                        children=text_to_children(item_text)
                    )
                )
            html_nodes.append(
                ParentNode(
                    tag="ul",
                    children=list_items
                )
            )
        elif block_type == BlockType.ordered_list:
            list_items = []
            for line in block.split("\n"):
                item_text = line[line.index(". ") + 2 :].strip()
                list_items.append(
                    ParentNode(
                        tag="li",
                        children=text_to_children(item_text)
                    )
                )
            html_nodes.append(
                ParentNode(
                    tag="ol",
                    children=list_items
                )
            )
        elif block_type == BlockType.quote:
            lines = block.split("\n")
            cleaned_lines = [line[2:].strip() for line in lines if line.startswith("> ")]
            quote_text = " ".join(cleaned_lines)
            html_nodes.append(
                ParentNode(
                    tag="blockquote",
                    children=text_to_children(quote_text)
                )
            )
        else:
            html_nodes.append(
            ParentNode(
                tag=block_type_to_html_tag(block_type),
                children=text_to_children(block)
            )
        )

    return ParentNode("div",html_nodes)