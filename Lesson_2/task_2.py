from os import path
import json


DIR = 'data'
FILE = 'orders.json'
PARAMS = ['item', 'quantity', 'price', 'buyer', 'date']


def read_json():
    with open(path.join(DIR, FILE)) as file:
        js_obj = json.load(file)
    return dict(js_obj)


def write_json(data):
    with open(path.join(DIR, FILE), 'w') as file:
        json.dump(data, file, indent=4)


def get_orders(data):
    key = next(iter(data.keys()))
    return data[key]


def input_orders():
    while True:
        item = {}
        for p in PARAMS:
            value = input(f'Enter {p}:\n')
            item[p] = value
        yield item

        answer = input('Continue [Y/N]').upper()
        if answer == 'N':
            break


def add_orders(items=None):
    data = read_json()
    orders = get_orders(data)

    if items is None:
        items = input_orders()

    orders.extend(items)
    write_json(data)


def remove_order():
    data = read_json()
    orders = get_orders(data)

    print('\n'.join([f'{i}. {o}' for i, o in enumerate(orders, 1)]))
    index = int(input())
    if len(orders) < index:
        print('Index out of range')
        return

    answer = input('Continue [Y/N]').upper()
    if answer == 'N':
        return

    orders.pop(index-1)
    write_json(data)


def clear_orders():
    data = read_json()
    get_orders(data).clear()
    write_json(data)


def view_orders():
    data = read_json()
    print(json.dumps(data, indent=2))


ACTIONS = {
    'Add orders': add_orders,
    'Remove order': remove_order,
    'Clear orders': clear_orders,
    'View orders': view_orders
}


def main():
    actions_len = len(ACTIONS)
    actions_name = '\n'.join([f'{i}. {a}' for i, a in enumerate(ACTIONS.keys(), 1)])
    actions = list(ACTIONS.values())
    while True:
        answer = int(input(f'Select action:\n{actions_name}\n0. exit\n'))
        if answer == 0:
            return

        if answer <= actions_len:
            actions[answer-1]()
        else:
            print('Incorrect action')
        print('-'*30)


if __name__ == '__main__':
    main()
