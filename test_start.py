import subprocess


PORT = 7878


def add_subprocess(processes, cmd):
    processes.append(subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE))


def main():
    processes = []
    exit_flag = False

    while not exit_flag:

        action = input('Select action:\n S - start server\n '
                       'L - start client listen-mode\n '
                       'R - start client send-mode \n '
                       'Q - all stop and quit ').upper()

        if action == 'S':
            add_subprocess(processes, f'python server.py -p {PORT}')
        elif action == 'L':
            add_subprocess(processes, f'python client.py 127.0.0.1 {PORT}')
        elif action == 'R':
            add_subprocess(processes, f'python client.py 127.0.0.1 {PORT} S')
        elif action == 'Q':
            while processes:
                processes.pop().kill()


if __name__ == '__main__':
    main()
