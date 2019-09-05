"""
Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
"""

words = ['attribute', 'класс', 'функция', 'type']

e_words = []

for w in words:
    for c in w:
        if ord(c) > 255:
            e_words.append(w)
            break
print(f'Exception in:\n{e_words}')
