import os
from shutil import copy2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = 'common'

CLIENT_DIR = os.path.join(ROOT, 'client')
SERVER_DIR = os.path.join(ROOT, 'server')

EXCLUDE = ['__init__.py', '__pycache__']


def get_files(dir):
    for file in os.listdir(dir):
        if file in EXCLUDE:
            continue
        path = os.path.join(dir, file)
        dir_name = os.path.basename(dir)
        if os.path.isdir(path):
            for f in get_files(path):
                yield f
        else:
            yield path


def copy_file(new_file, file):
    if os.path.exists(new_file):
        os.remove(new_file)
    dir = os.path.dirname(new_file)
    if not os.path.exists(dir):
        os.makedirs(dir)

    copy2(file, new_file)


def main():
    common_dir = os.path.join(ROOT, DIR)
    files = list(get_files(common_dir))

    for f in files:
        file = os.path.relpath(f, common_dir)

        copy_file(os.path.join(CLIENT_DIR, file), f)
        copy_file(os.path.join(SERVER_DIR, file), f)


if __name__ == '__main__':
    main()
