"""
Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в
байтовое и выполнить обратное преобразование (используя методы encode и decode).
"""

words = ['разработка', 'администрирование', 'protocol', 'standard']

for w in words:
    encoded = w.encode()
    decoded = encoded.decode()
    print(f'{w} | {encoded} | {decoded}')
