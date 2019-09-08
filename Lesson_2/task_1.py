from os import path
import csv
import re


DIR = 'data'
FILES = ['info_1.txt', 'info_2.txt', 'info_3.txt']
OUTPUT_FILE = 'report.csv'
PARAMS = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']


def gen_regex_str():
    regex_parts = []
    for i, p in enumerate(PARAMS):
        regex_parts.append(rf'(^{p}:\s*(?P<p_{i}>.*)$)')
    return '|'.join(regex_parts)


def parse_file(file, pattern, size):
    with open(path.join(DIR,file), encoding='cp1251') as file:
        content = file.read()

    matches = re.finditer(pattern, content)
    result = list(['']*size)

    for m in matches:
        for i in range(size):
            eq = m[f'p_{i}']
            if eq is not None:
                result[i] = eq.strip()
                break
    return result


def get_data():
    pattern = re.compile(gen_regex_str(), re.MULTILINE)
    size = len(PARAMS)
    report = [PARAMS]

    for f in FILES:
        report.append(parse_file(f, pattern, size))
    return report


def write_csv(data):
    with open(path.join(DIR, OUTPUT_FILE), 'w+', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for d in data:
            writer.writerow(d)


def main():
    write_csv(get_data())


if __name__ == '__main__':
    main()
