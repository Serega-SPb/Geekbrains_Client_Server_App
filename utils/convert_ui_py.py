import os
from subprocess import call

COMMAND = 'python -m PyQt5.uic.pyuic -x INPUT -o OUTPUT'


def main():
    directory = input('Enter directory\n')
    source = input('Enter .ui file\n')
    result = input('Enter output .py file\n')

    source = os.path.join(directory, source)
    result = os.path.join(directory, result)

    cmd = COMMAND.replace('INPUT', source).replace('OUTPUT', result)
    call(cmd)


if __name__ == '__main__':
    main()
