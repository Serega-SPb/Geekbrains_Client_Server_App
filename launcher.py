import subprocess

CLIENT_FILE = 'client\\start_client.py'
SERVER_FILE = 'server\\start_server.py'


def add_subprocess(processes, cmd):
    processes.append(subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE))


def main():
    processes = []
    port = 7878
    exit_flag = False

    while not exit_flag:

        action = input('Select action:\n '
                       'S - start server\n '
                       'C - start client\n '
                       'P - set port (default=7878)\n '
                       'Q - all stop and quit\n').upper()

        if action == 'S':
            add_subprocess(processes, f'python {SERVER_FILE} -p {port}')
        elif action == 'C':
            add_subprocess(processes, f'python {CLIENT_FILE} 127.0.0.1 {port}')
        elif action == 'P':
            p = input('Enter port: ')
            if not p.isdigit() or not (1024 <= int(p) <= 65535):
                print('Incorrect input')
            else:
                port = p
        elif action == 'Q':
            while processes:
                processes.pop().kill()
            exit(0)


if __name__ == '__main__':
    main()
