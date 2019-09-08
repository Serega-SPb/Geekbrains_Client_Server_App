from os import path
import yaml

DIR = 'data'
FILE = 'test.yaml'

TEST_DICT = {
    'list': [1, 2, 3, 4, 5, 6, 7, 8, 9],
    'int': 10,
    'd': '$',
    'e': '€',
    'dict': {
        1: '一',
        2: '二',
        3: '三',
        4: '四',
        5: '五',
    }
}
print('Source')
print(TEST_DICT)

with open(path.join(DIR, FILE), 'w', encoding='utf-8') as file:
    yaml.dump(TEST_DICT, file, allow_unicode=True)


with open(path.join(DIR, FILE), 'r', encoding='utf-8') as file:
    content = yaml.load(file, yaml.FullLoader)

print('Loaded')
print(content)

print(f'Is equals: {TEST_DICT == content}')
