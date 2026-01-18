from textnode import TextNode, TextType

def main():
    textnode = TextNode("this is some anchor text", TextType.links, "https://www.boot.dev/")
    print(textnode)

main()