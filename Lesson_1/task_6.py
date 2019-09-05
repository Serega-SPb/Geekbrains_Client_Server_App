"""
Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.
"""


filename = 'test_file.txt'
lines = ['сетевое программирование', 'сокет', 'декоратор']

with open(filename, 'w+', encoding='utf-8') as w_file:  # default encoding: windows-1251
    for line in lines:
        w_file.write(line)
        w_file.write('\n')

with open(filename, 'r', encoding='utf-8') as r_file:
    for r in r_file.readlines():
        print(r, end='')


'''
import chardet


with open(filename, 'w+') as w_file:
    for line in lines:
        w_file.write(line)
        w_file.write('\n')

with open(filename, 'rb') as r_file:
    content = bytearray()
    for r in r_file.read():
        content.append(r)

    if len(content) > 0:
        enc = chardet.detect(content)['encoding']
        print(content.decode(enc))
'''

