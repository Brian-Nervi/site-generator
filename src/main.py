import shutil
import os

def clean_public():
    shutil.rmtree("public", ignore_errors=True)

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


def main():
    clean_public()
    copy_files_recursive("./static", "./public")
    pass

main()