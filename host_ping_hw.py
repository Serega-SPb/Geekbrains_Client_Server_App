from subprocess import Popen, PIPE
from ipaddress import ip_address
from tabulate import tabulate


AVAILABLE = 'Узел доступен'
UNAVAILABLE = 'Узел недоступен'


def ping(ip):
    with Popen(f'ping -n 1 {str(ip)}', stdout=PIPE) as pipe:
        return pipe.wait()


def host_ping(hosts):
    for ip in hosts:
        r = ping(ip)
        print(f'{ip} - {AVAILABLE if r == 0 else UNAVAILABLE}')


def host_range_ping(ip, ip_range):
    for _ in range(ip_range):
        r = ping(ip)
        print(f'{ip} - {AVAILABLE if r == 0 else UNAVAILABLE}')
        ip = ip + 1


def host_range_ping_tab(ip, ip_range):
    headers = ['Ip address', 'Status']
    result = []
    print()
    for _ in range(ip_range):
        r = ping(ip)
        result.append((ip, AVAILABLE if r == 0 else UNAVAILABLE))
        ip = ip + 1
    print(tabulate(result, headers=headers, tablefmt='grid'))
    print()
    alt_result = {
        AVAILABLE: [r[0] for r in result if r[1] == AVAILABLE],
        UNAVAILABLE: [r[0] for r in result if r[1] == UNAVAILABLE]
    }
    print(tabulate(alt_result, headers='keys', tablefmt='grid'))


ID = 'id'
DESC = 'description'
ACTION = 'action'

tasks = [
    {ID: 1, DESC: 'host ping', ACTION: host_ping},
    {ID: 2, DESC: 'host range ping', ACTION: host_range_ping},
    {ID: 3, DESC: 'host range ping tab', ACTION: host_range_ping_tab},
    {ID: 0, DESC: 'exit'}
]


def main():
    while True:
        print('Select task:')
        task_id = int(input('\n'.join([f'{t[ID]}. {t[DESC]}' for t in tasks])))
        if task_id == 0:
            return

        task = [t for t in tasks if t[ID] == task_id]
        if len(task) == 0:
            print('Incorrect task')
            break

        action = task[0][ACTION]

        if task_id == 1:
            hosts = []
            while True:
                addr = input('Enter address: ("" - exit)')
                if not addr:
                    break
                try:
                    hosts.append(ip_address(addr))
                except:
                    print('Incorrect input')
            action(hosts)
        elif task_id in [2, 3]:
            ip = ip_address(input('Enter first ip address: '))
            ip_range = int(input('Enter address range: '))
            action(ip, ip_range)


if __name__ == '__main__':
    main()
