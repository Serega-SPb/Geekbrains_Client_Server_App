"""
Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность
кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.
"""

import sys

words = ['class', 'function', 'method']
b_words = [b'class', b'function', b'method']


for w in words:
    print(f'{w} | {type(w)} | {len(w)}')

print(f'{"???":-^15}')
for i in range(len(words)):
    print(f'Size of "{words[i]}" Str-{sys.getsizeof(words[i])} Bytes-{sys.getsizeof(b_words[i])}')
