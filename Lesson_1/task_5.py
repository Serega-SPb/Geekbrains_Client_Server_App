"""
Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый тип на
кириллице.
"""

import subprocess
import chardet


command = 'ping'
urls = ['yandex.ru', 'youtube.com', 'google.com']
output_lines = []
curr_encoding = None

for i in range(len(urls)):
    stream = subprocess.Popen([command, urls[i]], stdout=subprocess.PIPE)
    output_lines.extend(stream.stdout)
    output_lines.append(b'='*10 + b'\n')

for line in output_lines:
    if line.isspace():
        continue
    if curr_encoding is None:
        curr_encoding = chardet.detect(line)['encoding']
        print(f'Curr ENCODING: {curr_encoding}')

    print(line.decode(curr_encoding), end='')

'''
Win 10 x64: Curr ENCODING: IBM866
Raspbian 9: Curr ENCODING: ascii
'''