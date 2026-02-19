import shutil
import os
import sys
from blocks import markdown_to_html_node

def clean_docs():
    shutil.rmtree("docs", ignore_errors=True)

def copy_files_recursive(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for filename in os.listdir(src):
        src_path = os.path.join(src, filename)
        dst_path = os.path.join(dst, filename)
        print(f"Copying {src_path} to {dst_path}")
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)
        elif os.path.isdir(src_path):
            copy_files_recursive(src_path, dst_path)

def extract_title(markdown):
    for line in markdown.splitlines():
        if line.lstrip().startswith("# "):
            return line.lstrip()[2:].strip()
    raise Exception("Title not found in markdown")

def generate_page(from_path, template_path, dest_path, basepath=None):
    print(f"Generating page from {from_path} to {dest_path} using template {template_path}")
    with open(from_path, "r") as file:
        markdown = file.read()
    with open(template_path, "r") as template:
        template_content = template.read()
    html = markdown_to_html_node(markdown).to_html()
    if html.startswith("<div>") and html.endswith("</div>"):
        html = html[len("<div>") : -len("</div>")]
    title = extract_title(markdown)
    page_content = template_content.replace("{{ Content }}", html).replace("{{ Title }}", title)
    if basepath:
        page_content = page_content.replace('href="/', f'href="{basepath}')
        page_content = page_content.replace('src="/', f'src="{basepath}')
    final_dest_path = os.path.dirname(dest_path)
    if final_dest_path:
        if not os.path.exists(final_dest_path):
            os.makedirs(final_dest_path)
    with open(dest_path, "w") as f:
        f.write(page_content)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath=None):
    for file in os.listdir(dir_path_content):
        entry = os.path.join(dir_path_content, file) #makes it a full path
        if os.path.isdir(entry):
            generate_pages_recursive(entry, template_path, os.path.join(dest_dir_path, file), basepath)
        if os.path.isfile(entry) and entry.endswith(".md"):
            generate_page(entry, template_path, os.path.join(dest_dir_path, file[:-3] + ".html"), basepath)


    

def main():
    clean_docs()
    copy_files_recursive("./static", "./docs")
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    generate_pages_recursive("./content", "./template.html", "./docs", basepath)

    
    pass

main()